import pytest
from addressbook.models import AddressBook
from addressbook.book_storage import BookStorage
from addressbook.handler import handle


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def book(tmp_path, monkeypatch):
    monkeypatch.setattr(BookStorage, "_storage_dir", tmp_path)
    return AddressBook("json")


@pytest.fixture
def book_with_contact(book):
    handle(book, "add", ["Alice", "0671234567"])
    return book


# ---------------------------------------------------------------------------
# Unknown / invalid commands
# ---------------------------------------------------------------------------

class TestInvalidCommands:
    def test_unknown_command(self, book, capsys):
        handle(book, "foobar", [])
        assert "foobar" in capsys.readouterr().out

    def test_wrong_arg_count(self, book, capsys):
        handle(book, "add", ["Alice"])
        out = capsys.readouterr().out
        assert "Invalid arguments" in out


# ---------------------------------------------------------------------------
# hello
# ---------------------------------------------------------------------------

class TestHello:
    def test_hello(self, book, capsys):
        handle(book, "hello", [])
        assert "Hello" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# add / phone / change / delete
# ---------------------------------------------------------------------------

class TestContactCommands:
    def test_add_contact(self, book, capsys):
        handle(book, "add", ["Bob", "0991112233"])
        assert "Bob" in book.data

    def test_add_contact_success_message(self, book, capsys):
        handle(book, "add", ["Bob", "0991112233"])
        assert "saved" in capsys.readouterr().out

    def test_add_invalid_phone(self, book, capsys):
        handle(book, "add", ["Bob", "123"])
        assert "Bob" not in book.data

    def test_phone_lookup(self, book_with_contact, capsys):
        handle(book_with_contact, "phone", ["0671234567"])
        assert "Alice" in capsys.readouterr().out

    def test_phone_not_found(self, book, capsys):
        handle(book, "phone", ["0000000000"])
        out = capsys.readouterr().out
        assert "not found" in out.lower() or "0000000000" in out

    def test_change_phone(self, book_with_contact, capsys):
        handle(book_with_contact, "change", ["Alice", "0671234567", "0991112233"])
        assert book_with_contact.data["Alice"].find_phone("0991112233") is not None

    def test_change_contact_not_found(self, book, capsys):
        handle(book, "change", ["Ghost", "0671234567", "0991112233"])
        assert "Ghost" in capsys.readouterr().out

    def test_delete_contact(self, book_with_contact, capsys):
        handle(book_with_contact, "delete", ["Alice"])
        assert "Alice" not in book_with_contact.data

    def test_delete_not_found(self, book, capsys):
        handle(book, "delete", ["Ghost"])
        assert "Ghost" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# birthday
# ---------------------------------------------------------------------------

class TestBirthdayCommands:
    def test_add_birthday(self, book_with_contact, capsys):
        handle(book_with_contact, "add-birthday", ["Alice", "15.03.1990"])
        assert str(book_with_contact.data["Alice"].birthday) == "15.03.1990"

    def test_add_invalid_birthday(self, book_with_contact, capsys):
        handle(book_with_contact, "add-birthday", ["Alice", "1990-03-15"])
        assert book_with_contact.data["Alice"].birthday is None

    def test_show_birthday(self, book_with_contact, capsys):
        handle(book_with_contact, "add-birthday", ["Alice", "15.03.1990"])
        capsys.readouterr()
        handle(book_with_contact, "show-birthday", ["Alice"])
        assert "Alice" in capsys.readouterr().out

    def test_birthdays_default(self, book_with_contact, capsys):
        handle(book_with_contact, "birthdays", [])
        assert "DOB" in capsys.readouterr().out

    def test_birthdays_custom_days(self, book_with_contact, capsys):
        handle(book_with_contact, "birthdays", ["30"])
        assert "30" in capsys.readouterr().out

    def test_birthdays_invalid_days(self, book_with_contact, capsys):
        handle(book_with_contact, "birthdays", ["abc"])
        assert "positive integer" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# email / address
# ---------------------------------------------------------------------------

class TestEmailAddressCommands:
    def test_add_email(self, book_with_contact, capsys):
        handle(book_with_contact, "add-email", ["Alice", "alice@example.com"])
        assert str(book_with_contact.data["Alice"].email) == "alice@example.com"

    def test_add_invalid_email(self, book_with_contact, capsys):
        handle(book_with_contact, "add-email", ["Alice", "not-an-email"])
        assert book_with_contact.data["Alice"].email is None

    def test_edit_email(self, book_with_contact, capsys):
        handle(book_with_contact, "add-email", ["Alice", "alice@example.com"])
        handle(book_with_contact, "edit-email", ["Alice", "new@example.com"])
        assert str(book_with_contact.data["Alice"].email) == "new@example.com"

    def test_add_address(self, book_with_contact, capsys):
        handle(book_with_contact, "add-address", ["Alice", "12", "Baker", "Street"])
        assert book_with_contact.data["Alice"].address is not None

    def test_edit_address(self, book_with_contact, capsys):
        handle(book_with_contact, "add-address", ["Alice", "12", "Baker", "Street"])
        handle(book_with_contact, "edit-address", ["Alice", "99", "Main", "Ave"])
        assert "99 Main Ave" in str(book_with_contact.data["Alice"].address)


# ---------------------------------------------------------------------------
# notes
# ---------------------------------------------------------------------------

class TestNoteCommands:
    def test_add_note(self, book_with_contact, capsys):
        handle(book_with_contact, "add-note", ["Alice", "call", "alice", "tomorrow"])
        assert len(book_with_contact.data["Alice"].notes) == 1

    def test_add_note_success_message(self, book_with_contact, capsys):
        handle(book_with_contact, "add-note", ["Alice", "some", "note"])
        assert "added" in capsys.readouterr().out

    def test_edit_note(self, book_with_contact, capsys):
        handle(book_with_contact, "add-note", ["Alice", "call", "alice", "tomorrow"])
        title = book_with_contact.data["Alice"].notes[0].title
        handle(book_with_contact, "edit-note", ["Alice", title, "updated", "content"])
        assert book_with_contact.data["Alice"].notes[0].content == "updated content"

    def test_remove_note(self, book_with_contact, capsys):
        handle(book_with_contact, "add-note", ["Alice", "call", "alice", "tomorrow"])
        title = book_with_contact.data["Alice"].notes[0].title
        handle(book_with_contact, "remove-note", ["Alice", title])
        assert len(book_with_contact.data["Alice"].notes) == 0

    def test_remove_note_not_found(self, book_with_contact, capsys):
        handle(book_with_contact, "remove-note", ["Alice", "nonexistent_title"])
        assert "nonexistent_title" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# find
# ---------------------------------------------------------------------------

class TestFindCommand:
    def test_find_existing(self, book_with_contact, capsys):
        handle(book_with_contact, "find", ["alice"])
        assert "alice" in capsys.readouterr().out.lower()

    def test_find_no_results(self, book_with_contact, capsys):
        handle(book_with_contact, "find", ["xyz_not_exist"])
        assert "No results" in capsys.readouterr().out

    def test_find_multiword_query(self, book, capsys):
        handle(book, "add", ["John Doe", "0671234567"])
        capsys.readouterr()
        handle(book, "find", ["john", "doe"])
        assert "John Doe" in capsys.readouterr().out
