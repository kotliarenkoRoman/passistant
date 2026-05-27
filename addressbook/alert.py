from colorama import Fore
from enum import Enum, auto


class AlertType(Enum):
    SUCCESS = auto()
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    MUTED = auto()


class Alert:
    @staticmethod
    def msg(text: str, alert_type: AlertType) -> str:
        match alert_type:
            case AlertType.SUCCESS:
                return f"{Fore.GREEN}{text}{Fore.RESET}"
            case AlertType.INFO:
                return f"{Fore.BLUE}{text}{Fore.RESET}"
            case AlertType.MUTED:
                return f"{Fore.LIGHTBLACK_EX}{text}{Fore.RESET}"
            case AlertType.WARN:
                return f"{Fore.YELLOW}{text}{Fore.RESET}"
            case AlertType.ERROR:
                return f"{Fore.RED}{text}{Fore.RESET}"
            case _:
                return text

    @staticmethod
    def show(text: str, alert_type: AlertType) -> None:
        print(Alert.msg(text, alert_type))
