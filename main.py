import shlex
from addressbook import AddressBook, Alert, AlertType
from addressbook.handler import handle
import readline
import atexit
from pathlib import Path

HISTORY_FILE = Path(".cli_history")


def setup_readline() -> None:
    """Setup history and tab completion."""
    if HISTORY_FILE.exists():
        readline.read_history_file(HISTORY_FILE)
    readline.set_history_length(1000)
    atexit.register(readline.write_history_file, HISTORY_FILE)


def parse_input(response: str):
    params = shlex.split(response.strip())
    command = params[0]
    args = params[1:]
    return command.lower(), args


def main():
    setup_readline()
    book = AddressBook("json")

    Alert.show("Welcome to assistant bot!", alert_type=AlertType.INFO)
    while True:
        try:
            response = input("Enter command: ").strip()
        except KeyboardInterrupt:
            print()
            if readline.get_line_buffer():
                continue
            Alert.show("Good bye!", AlertType.SUCCESS)
            break

        if not response:
            continue
        if response in ("exit", "close"):
            Alert.show("Good bye!", AlertType.SUCCESS)
            break

        cmd, args = parse_input(response)
        handle(book, cmd, args)


if __name__ == "__main__":
    main()
