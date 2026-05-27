from .models import AddressBook
from .alert import Alert, AlertType
from .exceptions import (
    AddressBookError,
)
from functools import wraps

#: Supported CLI commands with their required attributes.
CMDS = {
    "hello": {"attrs": []},
    "add": {"attrs": ["name", "phone"]},
    "phone": {"attrs": ["phone"]},
    "change": {"attrs": ["name", "phone", "new_phone"]},
    "delete": {"attrs": ["name"]},
    "all": {"attrs": []},
    "add-birthday": {"attrs": ["name", "birthday"]},
    "show-birthday": {"attrs": ["name"]},
    "birthdays": {"attrs": [], "optional": True},
    "add-email": {"attrs": ["name", "email"]},
    "edit-email": {"attrs": ["name", "email"]},
    "add-address": {"attrs": ["name", "address"], "plural": True},
    "edit-address": {"attrs": ["name", "address"], "plural": True},
    "add-note":    {"attrs": ["name", "content"], "plural": True},
    "remove-note": {"attrs": ["name", "title"]},
    "edit-note":   {"attrs": ["name", "title", "content"], "plural": True},
    "find":        {"attrs": ["query"], "plural": True},
}


def validate_attrs(func):
    """Decorator for validating command attributes before execution."""

    @wraps(func)
    def wrapper(*args, **kwargs):

        book, cmd_name, attrs = args
        cmd = CMDS.get(cmd_name)

        if not cmd:
            Alert.show(f"Unknow command: '{cmd_name}'", AlertType.ERROR)
            return

        expected = cmd.get("attrs", [])
        is_plural = cmd.get("plural", False)
        is_optional = cmd.get("optional", False)
        invalid = (
            len(attrs) < len(expected) if (is_plural or is_optional) else len(attrs) != len(expected)
        )

        if invalid:
            last = f"[{expected[-1]}...]" if is_plural else f"[{expected[-1]}]"
            attrs_string = " ".join(f"[{i}]" for i in expected[:-1]) + f" {last}"
            Alert.show(
                f"Invalid arguments for '{cmd_name}'. Usage: {cmd_name} {attrs_string}",
                AlertType.ERROR,
            )
            return

        if is_plural:
            merged = list(attrs[: len(expected) - 1]) + [
                " ".join(attrs[len(expected) - 1 :])
            ]
            return func(book, cmd_name, merged)

        return func(*args, **kwargs)

    return wrapper


@validate_attrs
def handle(book: AddressBook, name: str, attr: list | None):
    """Handle and dispatch CLI commands to the corresponding AddressBook operations."""
    try:
        match name:
            case "hello":
                Alert.show("Hello, how can i help you?", AlertType.SUCCESS)
            case "add":
                person_name, phone = attr
                book.add(person_name, phone)
                Alert.show(f"Contact {person_name} saved", AlertType.SUCCESS)
            case "phone":
                Alert.show(str(book.find_by("phone", attr[0])), AlertType.INFO)
            case "change":
                person_name, phone, new_phone = attr
                book.change(person_name, phone, new_phone)
                Alert.show(
                    f"Phone updated for {person_name}: {phone} to {new_phone}",
                    AlertType.SUCCESS,
                )
            case "delete":
                name = attr[0]
                book.delete(name)
                Alert.show(
                    f"Contact '{name}' was successfully deleted", AlertType.SUCCESS
                )
            case "add-birthday":
                person_name, birthday = attr
                book.add_birthday(person_name, birthday)
                Alert.show(
                    f"Birthday date added for the: {person_name}", AlertType.SUCCESS
                )
            case "show-birthday":
                Alert.show(str(book.find_by("name", attr[0])), AlertType.SUCCESS)
            case "add-email" | "edit-email":
                person_name, email = attr
                book.store_email(person_name, email)
                Alert.show(f"Email updated for the: {person_name}", AlertType.SUCCESS)
            case "add-address" | "edit-address":
                person_name, address = attr
                book.store_address(person_name, address)
                Alert.show(f"Address updated for the: {person_name}", AlertType.SUCCESS)
            case "add-note":
                person_name, content = attr
                book.add_note(person_name, content)
                Alert.show(f"Note added for {person_name}", AlertType.SUCCESS)
            case "remove-note":
                person_name, title = attr
                book.remove_note(person_name, title)
                Alert.show(f"Note '{title}' removed from {person_name}", AlertType.SUCCESS)
            case "edit-note":
                person_name, title, content = attr
                book.edit_note(person_name, title, content)
                Alert.show(f"Note '{title}' updated for {person_name}", AlertType.SUCCESS)
            case "find":
                query = attr[0]
                results = book.find(query)
                if not results:
                    Alert.show(f"No results for '{query}'", AlertType.MUTED)
                else:
                    Alert.show(f"Found {len(results)} contact(s):", AlertType.WARN)
                    print(book._render_table(results))
            case "all":
                book.all()
            case "birthdays":
                try:
                    days = int(attr[0]) if attr else 7
                    if days <= 0:
                        raise ValueError
                except ValueError:
                    Alert.show("Days must be a positive integer. Usage: birthdays [days]", AlertType.ERROR)
                    return
                book.birthdays(days)
            case _:
                Alert.show("Invalid command", AlertType.ERROR)
    except (ValueError, AddressBookError) as e:
        Alert.show(str(e), AlertType.ERROR)
    except TypeError:
        Alert.show(f"Invalid arguments for '{name}'", AlertType.ERROR)
