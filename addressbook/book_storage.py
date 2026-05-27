import pickle
import json
from pathlib import Path
from abc import ABC, abstractmethod


class BookStorage(ABC):
    _storage_dir = Path.home() / ".passistant"
    filename = "./addressbook/storage/addressbook"

    def __init__(self):
        self.filepath = self.get_filepath()

    def get_filepath(self) -> Path:
        infix = "json" if isinstance(self, JsonStorage) else "pkl"
        path = self._storage_dir / f"addressbook.{infix}"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @abstractmethod
    def load_data() -> dict:
        pass

    @abstractmethod
    def save_data(data: dict) -> None:
        pass


class PickleStorage(BookStorage):
    def __init__(self):
        super().__init__()

    def load_data(self) -> dict:
        try:
            with open(self.filepath, "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):
            return {}

    def save_data(self, data: dict) -> None:
        try:
            with open(self.filepath, "wb") as f:
                pickle.dump(data, f)
        except (PermissionError, Exception) as e:
            print(str(e))


class JsonStorage(BookStorage):
    def __init__(self):
        super().__init__()

    def load_data(self) -> dict:
        try:
            from .models import Record

            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
                return {name: Record.from_dict(data) for name, data in raw.items()}
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def save_data(self, data: dict) -> None:
        try:
            serialized = {name: record.to_dict() for name, record in data.items()}
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)
        except (PermissionError, Exception) as e:
            print(str(e))
