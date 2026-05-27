from collections import UserDict
from colorama import Fore
from datetime import datetime as dt
from functools import wraps
from prettytable import PrettyTable


from .alert import Alert, AlertType
from .exceptions import (
    AddressBookError,
    ContactNotFoundError,
    PhoneNotFoundError,
    ContactAlreadyExistsError,
    PhoneExistsError,
    NoteNotFoundError,
)
from .utils import Config, Utils
from .book_storage import BookStorage, PickleStorage, JsonStorage


class Name:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, name: str):
        if len(name) < 3:
            raise ValueError("Name must be at least 3 symbols")
        self._value = name

    def __str__(self):
        return self.value


class Phone:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, phone: str):
        if not phone.isdigit():
            raise ValueError("Phone must be a digits")
        if not len(phone) == 10:
            raise ValueError("Phone must be a 10 number digits")
        self._value = phone


class Birthday:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, dob: str):
        try:
            self._value = dt.strptime(dob, Config.DATE_FORMAT.value)
        except:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        if not self._value:
            return "--"
        dob_dt = self._value.date()
        return dob_dt.strftime(Config.DATE_FORMAT.value)


class Email:
    def __init__(self, value: str):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, email: str):
        if not Utils.validate_email(email):
            raise ValueError(f"Invalid email: {email}")
        self._value = email

    def __str__(self):
        return str(self.value)


class Address:
    def __init__(self, value: str):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, address: str):
        if len(address) < 5:
            raise ValueError("Address must have at least 5 symbols")
        self._value = address

    def __str__(self):
        return str(self.value)


class Note:
    def __init__(self, title: str, content: str, date: dt = None):
        self.title = title
        self.content = content
        self.date = date or dt.now()

    def to_dict(self) -> dict:
        return {"date": self.date.isoformat(), "title": self.title, "content": self.content}

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        n = cls(data["title"], data["content"])
        n.date = dt.fromisoformat(data["date"])
        return n

    def __str__(self):
        return f"{self.date.strftime('%d.%m.%Y %H:%M')} [{self.title}]: {self.content}"


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.address = None
        self.email = None
        self.notes: list[Note] = []

    def add_phone(self, phone: str) -> None:
        if self.find_phone(phone):
            raise PhoneExistsError(phone, self.name.value)
        self.phones.append(Phone(phone))

    def find_phone(self, phone: str):
        return next((x for x in self.phones if x.value == phone), None)

    def edit_phone(self, current_phone: str, new_phone: str):
        idx = next(
            (i for i, p in enumerate(self.phones) if p.value == current_phone), None
        )
        if idx is None:
            raise PhoneNotFoundError(current_phone)
        self.phones[idx] = Phone(new_phone)

    def remove_phone(self, phone: str):
        exists = self.find_phone(phone)
        if not exists:
            raise PhoneNotFoundError(phone)
        self.phones.remove(exists)

    def add_birthday(self, dob: str) -> None:
        self.birthday = Birthday(dob)

    def show_birthday(self) -> str | None:
        return self.birthday

    def store_address(self, address: str) -> None:
        self.address = Address(address)

    def store_email(self, email: str) -> None:
        self.email = Email(email)

    def add_note(self, content: str) -> None:
        base = Utils.generate_note_title(content)
        title, counter = base, 2
        while self._find_note(title):
            title = f"{base}_{counter}"
            counter += 1
        self.notes.append(Note(title, content))

    def remove_note(self, title: str) -> None:
        note = self._find_note(title)
        if not note:
            raise NoteNotFoundError(title)
        self.notes.remove(note)

    def edit_note(self, title: str, content: str) -> None:
        note = self._find_note(title)
        if not note:
            raise NoteNotFoundError(title)
        note.content = content
        note.date = dt.now()

    def _find_note(self, title: str) -> "Note | None":
        return next((n for n in self.notes if n.title == title), None)

    def to_dict(self) -> dict:
        """Serialize record to dictionary for JSON storage."""

        return {
            "name": self.name.value,
            "phones": [p.value for p in self.phones],
            "birthday": str(self.birthday) if self.birthday else None,
            "address": self.address.value if self.address else None,
            "email": self.email.value if self.email else None,
            "notes": [n.to_dict() for n in self.notes],
        }

    @classmethod
    def from_dict(cls, item: dict) -> Record:
        """Unserialize record from dictionary for JSON storage."""

        r = cls(item["name"])
        if item.get("birthday"):
            r.add_birthday(item["birthday"])
        if item.get("email"):
            r.store_email(item["email"])
        if item.get("address"):
            r.store_address(item["address"])
        for p in item.get("phones", []):
            r.add_phone(p)
        for n in item.get("notes", []):
            r.notes.append(Note.from_dict(n))
        return r

    def matches(self, query: str) -> bool:
        q = query.lower()
        fields = [
            self.name.value,
            str(self.birthday) if self.birthday else "",
            str(self.email) if self.email else "",
            str(self.address) if self.address else "",
            *[p.value for p in self.phones],
            *[n.title + " " + n.content for n in self.notes],
        ]
        return any(q in field.lower() for field in fields)

    def __str__(self):
        notes_str = "; ".join(str(n) for n in self.notes) or "--"
        return (
            f"{Fore.BLUE}Contact name:{Fore.RESET} {self.name.value}, "
            f"{Fore.YELLOW}DOB:{Fore.RESET} {self.birthday}, "
            f"{Fore.CYAN}Email:{Fore.RESET} {self.email}, "
            f"{Fore.BLUE}Address:{Fore.RESET} {self.address}, "
            f"{Fore.GREEN}phones:{Fore.RESET} {'; '.join(p.value for p in self.phones)}, "
            f"{Fore.MAGENTA}notes:{Fore.RESET} {notes_str}"
        )


class AddressBook(UserDict):
    def __init__(self, storageType=None):
        super().__init__()
        self.storage = self.set_storage(storageType)
        self.data: dict[str, Record] = self.storage.load_data()

    def set_storage(self, storageType: str) -> BookStorage:
        match storageType:
            case "json":
                return JsonStorage()
            case _:
                return PickleStorage()

    def savedata(func):
        """tracking save data for methods"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                book: AddressBook = args[0]
                book.storage.save_data(book.data)
                return res
            except Exception as e:
                raise AddressBookError(e)

        return wrapper

    @savedata
    def add(self, name: str, phone: str) -> None:
        r = self.data.get(name)
        """add phone to existed user"""
        if r:
            r.add_phone(phone)
            self.update(r)
            return
        """add new user record"""
        r = Record(name)
        r.add_phone(phone)
        self.add_record(r)

    @savedata
    def change(self, name: str, phone: str, new_phone: str) -> None:
        r = self.find_by("name", name)
        if not r:
            raise ContactNotFoundError(name)
        r.edit_phone(phone, new_phone)

    @savedata
    def delete(self, name) -> None:
        if name not in self.data:
            raise ContactNotFoundError(name)
        del self.data[name]

    @savedata
    def add_birthday(self, name: str, birthday: str) -> None:
        r = self.find_by("name", name)
        if not r:
            raise ContactNotFoundError(name)
        r.add_birthday(birthday)

    @savedata
    def store_email(self, name: str, email: str) -> None:
        r = self.find_by("name", name)
        if not r:
            raise ContactNotFoundError(name)
        r.store_email(email)

    @savedata
    def store_address(self, name: str, address: str) -> None:
        r = self.find_by("name", name)
        if not r:
            raise ContactNotFoundError(name)
        r.store_address(address)

    @savedata
    def add_note(self, name: str, content: str) -> None:
        r = self.find_by("name", name)
        r.add_note(content)

    @savedata
    def remove_note(self, name: str, title: str) -> None:
        r = self.find_by("name", name)
        r.remove_note(title)

    @savedata
    def edit_note(self, name: str, title: str, content: str) -> None:
        r = self.find_by("name", name)
        r.edit_note(title, content)

    def add_record(self, record: Record) -> None:
        if self.data.get(record.name.value):
            raise ContactAlreadyExistsError(record.name.value)
        self.data[record.name.value] = record

    def find_by(self, key: str, value: str) -> Record:
        """Find record by key and value."""
        match key:
            case "name" | "birthday":
                contact = self.data.get(value)
                if not contact:
                    raise ContactNotFoundError(value)
                return contact
            case "phone":
                contact = next(
                    (r for r in self.data.values() if r.find_phone(value)), None
                )
                if not contact:
                    raise PhoneNotFoundError(value)
                return contact
            case _:
                raise ContactNotFoundError(value)

    def update(self, record: Record):
        self.data[record.name.value] = record

    def _render_table(self, records) -> PrettyTable:
        headers = [
            f"{Fore.BLUE}Name{Fore.RESET}",
            f"{Fore.GREEN}Phones{Fore.RESET}",
            f"{Fore.YELLOW}Birthday{Fore.RESET}",
            f"{Fore.CYAN}Email{Fore.RESET}",
            f"{Fore.BLUE}Address{Fore.RESET}",
            f"{Fore.MAGENTA}Notes{Fore.RESET}",
        ]
        table = PrettyTable(headers)
        table.align = "l"
        for r in records:
            phones = "\n".join(p.value for p in r.phones) or "--"
            notes = "\n".join(n.title for n in r.notes) or "--"
            table.add_row([
                r.name.value,
                phones,
                str(r.birthday) if r.birthday else "--",
                str(r.email) if r.email else "--",
                str(r.address) if r.address else "--",
                notes,
            ])
        return table

    def find(self, query: str) -> list[Record]:
        return [r for r in self.data.values() if r.matches(query)]

    def all(self) -> None:
        """Show contacts list"""
        Alert.show("List of contacts:", AlertType.WARN)
        if not self.data:
            Alert.show("No users..", AlertType.MUTED)
        else:
            print(self._render_table(self.data.values()))

    def birthdays(self, days: int = 7) -> None:
        """Display contacts with upcoming birthdays within the next N days."""
        now = dt.today().date()

        congrats_dates = []
        for r in self.data.values():
            if not r.birthday:
                continue
            dob_this_year = r.birthday.value.replace(year=now.year).date()
            diff = (dob_this_year - now).days
            if not (0 <= diff <= days):
                continue
            is_weekend = dob_this_year.weekday() in Config.WEEKEND_DAYS.value
            congrats_date = Utils.shift_to_monday(now) if is_weekend else dob_this_year
            congrats_dates.append(
                {
                    "name": r.name.value,
                    "birthday": str(r.birthday),
                    "congratulation_date": congrats_date.strftime(
                        Config.DATE_FORMAT.value
                    ),
                }
            )

        Alert.show(f"Upcoming {days} days DOB ({len(congrats_dates)}):", AlertType.WARN)
        if not congrats_dates:
            Alert.show("Nobody..", AlertType.MUTED)
            return
        for item in congrats_dates:
            Alert.show(
                f"{item['name']} ({item['birthday']}): Congratulation date - {item['congratulation_date']}",
                AlertType.SUCCESS,
            )
