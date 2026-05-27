class AddressBookError(Exception):
    """Base exception"""


class ContactNotFoundError(AddressBookError):
    def __init__(self, name: str):
        super().__init__(f"Contact '{name}' not found")


class PhoneNotFoundError(AddressBookError):
    def __init__(self, phone: str):
        super().__init__(f"Phone '{phone}' not found")


class PhoneExistsError(AddressBookError):
    def __init__(self, phone: str, name: str):
        super().__init__(f"The user {name} already has phone number '{phone}'")


class ContactAlreadyExistsError(AddressBookError):
    def __init__(self, name: str):
        super().__init__(f"Contact '{name}' already exists")


class InvalidArgError(AddressBookError):
    def __init__(self, cmd_name: str, expected: str):
        super().__init__(f"Invalid arguments for '{cmd_name}'. {expected}")


class ValidationError(AddressBookError):
    pass


class NoteNotFoundError(AddressBookError):
    def __init__(self, title: str):
        super().__init__(f"Note '{title}' not found")
