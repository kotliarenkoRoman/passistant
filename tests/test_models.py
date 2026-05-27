import pytest
from addressbook.models import Record, AddressBook, Phone, Birthday, Email
from addressbook.book_storage import BookStorage
from addressbook.exceptions import (
    PhoneNotFoundError,
    PhoneExistsError,
    ContactNotFoundError,
    ContactAlreadyExistsError,
    NoteNotFoundError,
    AddressBookError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def book(tmp_path, monkeypatch):
    monkeypatch.setattr(BookStorage, "_storage_dir", tmp_path)
    return AddressBook("json")


@pytest.fixture
def record():
    r = Record("John Doe")
    r.add_phone("0671234567")
    return r


@pytest.fixture
def book_with_contact(book):
    book.add("Alice", "0671234567")
    return book


# ---------------------------------------------------------------------------
# Field validation
# ---------------------------------------------------------------------------

class TestPhoneValidation:
    def test_valid_phone(self):
        p = Phone("0671234567")
        assert p.value == "0671234567"

    def test_non_digits_raises(self):
        with pytest.raises(ValueError, match="digits"):
            Phone("067abc4567")

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError, match="10"):
            Phone("067123")


class TestBirthdayValidation:
    def test_valid_birthday(self):
        b = Birthday("15.03.1990")
        assert str(b) == "15.03.1990"

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="DD.MM.YYYY"):
            Birthday("1990-03-15")


class TestEmailValidation:
    def test_valid_email(self):
        e = Email("user@example.com")
        assert e.value == "user@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError, match="Invalid email"):
            Email("not-an-email")


# ---------------------------------------------------------------------------
# Record methods
# ---------------------------------------------------------------------------

class TestRecord:
    def test_name_too_short_raises(self):
        with pytest.raises(ValueError, match="3 symbols"):
            Record("Ab")

    def test_add_phone(self, record):
        record.add_phone("0991234567")
        assert len(record.phones) == 2

    def test_add_duplicate_phone_raises(self, record):
        with pytest.raises(PhoneExistsError):
            record.add_phone("0671234567")

    def test_find_phone_exists(self, record):
        assert record.find_phone("0671234567") is not None

    def test_find_phone_not_exists(self, record):
        assert record.find_phone("0000000000") is None

    def test_edit_phone(self, record):
        record.edit_phone("0671234567", "0991112233")
        assert record.find_phone("0991112233") is not None
        assert record.find_phone("0671234567") is None

    def test_edit_phone_not_found_raises(self, record):
        with pytest.raises(PhoneNotFoundError):
            record.edit_phone("0000000000", "0991112233")

    def test_remove_phone(self, record):
        record.remove_phone("0671234567")
        assert len(record.phones) == 0

    def test_remove_phone_not_found_raises(self, record):
        with pytest.raises(PhoneNotFoundError):
            record.remove_phone("0000000000")

    def test_add_birthday(self, record):
        record.add_birthday("15.03.1990")
        assert str(record.birthday) == "15.03.1990"

    def test_store_email(self, record):
        record.store_email("john@example.com")
        assert str(record.email) == "john@example.com"

    def test_store_address(self, record):
        record.store_address("12 Baker Street")
        assert str(record.address) == "12 Baker Street"

    def test_address_too_short_raises(self, record):
        with pytest.raises(ValueError, match="5 symbols"):
            record.store_address("abc")

    def test_add_note(self, record):
        record.add_note("buy some milk today")
        assert len(record.notes) == 1
        assert record.notes[0].content == "buy some milk today"

    def test_add_note_auto_title(self, record):
        record.add_note("buy some milk today")
        assert record.notes[0].title == "buy_some_milk"

    def test_add_note_duplicate_title_increments(self, record):
        record.add_note("buy some milk today")
        record.add_note("buy some milk tomorrow")
        assert record.notes[1].title == "buy_some_milk_2"

    def test_edit_note(self, record):
        record.add_note("buy some milk today")
        title = record.notes[0].title
        record.edit_note(title, "buy bread instead")
        assert record.notes[0].content == "buy bread instead"

    def test_edit_note_not_found_raises(self, record):
        with pytest.raises(NoteNotFoundError):
            record.edit_note("nonexistent_title", "content")

    def test_remove_note(self, record):
        record.add_note("buy some milk today")
        title = record.notes[0].title
        record.remove_note(title)
        assert len(record.notes) == 0

    def test_remove_note_not_found_raises(self, record):
        with pytest.raises(NoteNotFoundError):
            record.remove_note("nonexistent_title")


# ---------------------------------------------------------------------------
# Record.matches (search)
# ---------------------------------------------------------------------------

class TestRecordMatches:
    def test_matches_by_name(self, record):
        assert record.matches("john")

    def test_matches_case_insensitive(self, record):
        assert record.matches("JOHN")

    def test_matches_by_phone(self, record):
        assert record.matches("0671234567")

    def test_matches_partial_phone(self, record):
        assert record.matches("067")

    def test_matches_by_birthday(self, record):
        record.add_birthday("15.03.1990")
        assert record.matches("1990")

    def test_matches_by_email(self, record):
        record.store_email("john@example.com")
        assert record.matches("example.com")

    def test_matches_by_address(self, record):
        record.store_address("12 Baker Street")
        assert record.matches("baker")

    def test_matches_by_note_content(self, record):
        record.add_note("important meeting on friday")
        assert record.matches("meeting")

    def test_no_match(self, record):
        assert not record.matches("xyz_not_exist")


# ---------------------------------------------------------------------------
# AddressBook methods
# ---------------------------------------------------------------------------

class TestAddressBook:
    def test_add_new_contact(self, book):
        book.add("Alice", "0671234567")
        assert "Alice" in book.data

    def test_add_phone_to_existing_contact(self, book_with_contact):
        book_with_contact.add("Alice", "0991112233")
        assert len(book_with_contact.data["Alice"].phones) == 2

    def test_add_duplicate_phone_raises(self, book):
        book.add("Alice", "0671234567")
        with pytest.raises(AddressBookError):
            book.add("Alice", "0671234567")

    def test_change_phone(self, book_with_contact):
        book_with_contact.change("Alice", "0671234567", "0991112233")
        r = book_with_contact.data["Alice"]
        assert r.find_phone("0991112233") is not None
        assert r.find_phone("0671234567") is None

    def test_change_contact_not_found_raises(self, book):
        with pytest.raises(AddressBookError):
            book.change("Ghost", "0671234567", "0991112233")

    def test_delete_contact(self, book_with_contact):
        book_with_contact.delete("Alice")
        assert "Alice" not in book_with_contact.data

    def test_delete_not_found_raises(self, book):
        with pytest.raises(AddressBookError):
            book.delete("Ghost")

    def test_add_birthday(self, book_with_contact):
        book_with_contact.add_birthday("Alice", "15.03.1990")
        assert str(book_with_contact.data["Alice"].birthday) == "15.03.1990"

    def test_store_email(self, book_with_contact):
        book_with_contact.store_email("Alice", "alice@example.com")
        assert str(book_with_contact.data["Alice"].email) == "alice@example.com"

    def test_store_address(self, book_with_contact):
        book_with_contact.store_address("Alice", "12 Baker Street")
        assert str(book_with_contact.data["Alice"].address) == "12 Baker Street"

    def test_add_note(self, book_with_contact):
        book_with_contact.add_note("Alice", "call alice tomorrow")
        assert len(book_with_contact.data["Alice"].notes) == 1

    def test_edit_note(self, book_with_contact):
        book_with_contact.add_note("Alice", "call alice tomorrow")
        title = book_with_contact.data["Alice"].notes[0].title
        book_with_contact.edit_note("Alice", title, "call alice on monday")
        assert book_with_contact.data["Alice"].notes[0].content == "call alice on monday"

    def test_remove_note(self, book_with_contact):
        book_with_contact.add_note("Alice", "call alice tomorrow")
        title = book_with_contact.data["Alice"].notes[0].title
        book_with_contact.remove_note("Alice", title)
        assert len(book_with_contact.data["Alice"].notes) == 0

    def test_find_by_name(self, book_with_contact):
        results = book_with_contact.find("alice")
        assert len(results) == 1
        assert results[0].name.value == "Alice"

    def test_find_no_results(self, book_with_contact):
        results = book_with_contact.find("xyz_not_exist")
        assert results == []

    def test_find_multiple_results(self, book):
        book.add("Alice Smith", "0671234567")
        book.add("Bob Alice", "0991112233")
        results = book.find("alice")
        assert len(results) == 2

    def test_data_persists_after_reload(self, tmp_path, monkeypatch):
        monkeypatch.setattr(BookStorage, "_storage_dir", tmp_path)
        book1 = AddressBook("json")
        book1.add("Alice", "0671234567")

        book2 = AddressBook("json")
        assert "Alice" in book2.data
