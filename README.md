# Passistant — Personal Assistant CLI

A command-line personal assistant for managing contacts and notes. Data is stored persistently on disk and survives restarts.

## Features

- Store contacts with name, phones, email, address, and birthday
- Add multiple phone numbers per contact
- Add multiple tags per contact
- Attach notes to contacts with auto-generated titles
- Global search across all fields (name, phone, email, address, birthday, notes)
- Search only by Tags using `#<tag name>` in search query
- Upcoming birthday notifications for a configurable number of days
- Phone and email validation on input
- Pretty-printed color table output
- CLI history with arrow-key navigation
- Graceful Ctrl+C handling

## Requirements

- Python 3.10+

## Installation

```bash
git clone <repo-url>
cd passistant
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

Data is saved to `~/.passistant/addressbook.json` automatically after every change.

## Commands

> Names containing spaces must be wrapped in quotes: `"Alice Johnson"`

| Command          | Usage                         | Description                            |
|------------------|-------------------------------|----------------------------------------|
| `hello`          |                               | Greet the assistant                    |
| `add`            | `"name" [phone]`              | Add a new contact or phone to existing |
| `phone`          | `[phone]`                     | Find contact by phone number           |
| `change`         | `"name" [phone] [new_phone]`  | Change a contact's phone number        |
| `delete`         | `"name"`                      | Delete a contact                       |
| `all`            |                               | Show all contacts as a table           |
| `find`           | `[query...]`                  | Search across all fields               |
| `add-birthday`   | `"name" [DD.MM.YYYY]`         | Add birthday to a contact              |
| `show-birthday`  | `"name"`                      | Show full contact details              |
| `birthdays`      | `[days]`                      | Upcoming birthdays (default: 7 days)   |
| `add-email`      | `"name" [email]`              | Add email to a contact                 |
| `edit-email`     | `"name" [email]`              | Edit contact's email                   |
| `add-address`    | `"name" [address...]`         | Add address to a contact               |
| `edit-address`   | `"name" [address...]`         | Edit contact's address                 |
| `add-note`       | `"name" [content...]`         | Add a note to a contact                |
| `edit-note`      | `"name" [title] [content...]` | Edit a note by title                   |
| `remove-note`    | `"name" [title]`              | Remove a note by title                 |
| `add-tag`        | `"name" [tag]`                | Add a tag to a contact                 |
| `remove-tag`     | `"name" [tag]`                | Remove a tag from a contact            |
| `help`           |                               | Show command reference table           |
| `exit` / `close` |                               | Exit the assistant                     |

## Usage Examples

```
add "Alice Johnson" 0671234567
add-email "Alice Johnson" alice@example.com
add-address "Alice Johnson" 12 Baker Street, London
add-birthday "Alice Johnson" 15.03.1990
add-note "Alice Johnson" call alice about the project meeting
add-tag "Alice Johnson" weekly-meeting

find alice
find 1990
find gmail
-- find by tag only
find #weekly-meeting 

birthdays
birthdays 30

change "Alice Johnson" 0671234567 0991112233
delete "Alice Johnson"
```

## Project Structure

```
passistant/
├── addressbook/
│   ├── __init__.py        # Package exports
│   ├── models.py          # Record, AddressBook, field classes
│   ├── handler.py         # CLI command dispatch and validation
│   ├── book_storage.py    # JSON and Pickle storage backends
│   ├── alert.py           # Colored output helper
│   ├── exceptions.py      # Domain exceptions
│   └── utils.py           # Email validation, date helpers
├── tests/
│   ├── test_models.py     # Unit tests for models
│   └── test_handler.py    # Unit tests for CLI handler
├── main.py                # Entry point
└── requirements.txt
```

## Running Tests

```bash
# All tests
.venv/bin/pytest tests/ -v

# Short summary
.venv/bin/pytest tests/ -q

# Single file
.venv/bin/pytest tests/test_models.py -v

# Single test
.venv/bin/pytest tests/test_models.py::TestRecord::test_add_phone -v
```

## Validation Rules

- **Phone**: exactly 10 digits, numbers only
- **Email**: standard format (`user@domain.tld`)
- **Birthday**: `DD.MM.YYYY` format
- **Name**: minimum 3 characters
- **Tag**: minimum 3 characters
- **Address**: minimum 5 characters
