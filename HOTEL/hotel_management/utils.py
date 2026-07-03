"""
utils.py
--------
Utility functions and helpers used across the Hotel Management System.
Includes: coloured terminal output, input validators, logging, and display helpers.
"""

import os
import re
import sys
import logging
from datetime import datetime, date
from colorama import init, Fore, Back, Style

# Initialise colorama (autoreset so each print doesn't leak colour)
init(autoreset=True)

# ---------------------------------------------------------------------------
# Colour palette helpers
# ---------------------------------------------------------------------------

class Colors:
    """Thin wrappers around colorama colour codes for consistent styling."""

    HEADER   = Fore.CYAN    + Style.BRIGHT
    SUCCESS  = Fore.GREEN   + Style.BRIGHT
    WARNING  = Fore.YELLOW  + Style.BRIGHT
    ERROR    = Fore.RED     + Style.BRIGHT
    INFO     = Fore.WHITE   + Style.BRIGHT
    MENU     = Fore.MAGENTA + Style.BRIGHT
    LABEL    = Fore.BLUE    + Style.BRIGHT
    RESET    = Style.RESET_ALL
    DIM      = Style.DIM
    BOLD     = Style.BRIGHT
    CYAN     = Fore.CYAN
    GREEN    = Fore.GREEN
    YELLOW   = Fore.YELLOW
    RED      = Fore.RED
    MAGENTA  = Fore.MAGENTA
    BLUE     = Fore.BLUE
    WHITE    = Fore.WHITE

    @staticmethod
    def print_success(msg: str) -> None:
        print(f"{Fore.GREEN}{Style.BRIGHT}✔  {msg}{Style.RESET_ALL}")

    @staticmethod
    def print_error(msg: str) -> None:
        print(f"{Fore.RED}{Style.BRIGHT}✘  {msg}{Style.RESET_ALL}")

    @staticmethod
    def print_warning(msg: str) -> None:
        print(f"{Fore.YELLOW}{Style.BRIGHT}⚠  {msg}{Style.RESET_ALL}")

    @staticmethod
    def print_info(msg: str) -> None:
        print(f"{Fore.CYAN}{Style.BRIGHT}ℹ  {msg}{Style.RESET_ALL}")

    @staticmethod
    def print_header(msg: str) -> None:
        width = 54
        border = "═" * width
        print(f"\n{Fore.CYAN}{Style.BRIGHT}╔{border}╗")
        print(f"║{msg.center(width)}║")
        print(f"╚{border}╝{Style.RESET_ALL}")


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

LOG_DIR  = os.path.join(os.path.dirname(__file__), "..")   # project root
LOG_FILE = os.path.join(LOG_DIR, "logs.txt")


def _setup_logger() -> logging.Logger:
    """Configure and return a module-level file logger."""
    logger = logging.getLogger("HotelManagement")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


_logger = _setup_logger()


def log_event(level: str, message: str) -> None:
    """
    Log an event to logs.txt.

    Args:
        level:   'info', 'warning', 'error', or 'debug'
        message: Human-readable description of the event.
    """
    level = level.lower()
    if level == "info":
        _logger.info(message)
    elif level == "warning":
        _logger.warning(message)
    elif level == "error":
        _logger.error(message)
    elif level == "debug":
        _logger.debug(message)
    else:
        _logger.info(message)


# ---------------------------------------------------------------------------
# Input validators
# ---------------------------------------------------------------------------

def validate_phone(phone: str) -> bool:
    """Phone must be 7–15 digits (allows optional leading +)."""
    return bool(re.fullmatch(r"\+?\d{7,15}", phone.strip()))


def validate_email(email: str) -> bool:
    """Basic e-mail pattern check."""
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.fullmatch(pattern, email.strip()))


def validate_date(date_str: str) -> bool:
    """Return True if date_str is a valid YYYY-MM-DD date string."""
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def parse_date(date_str: str) -> date:
    """Parse a YYYY-MM-DD string into a date object."""
    return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()


def validate_dates(check_in_str: str, check_out_str: str) -> tuple[bool, str]:
    """
    Validate that check-in and check-out dates are valid and in the correct order.

    Returns:
        (True, "") if valid; (False, reason) otherwise.
    """
    if not validate_date(check_in_str):
        return False, "Check-in date is not valid. Use YYYY-MM-DD format."
    if not validate_date(check_out_str):
        return False, "Check-out date is not valid. Use YYYY-MM-DD format."
    ci = parse_date(check_in_str)
    co = parse_date(check_out_str)
    if co <= ci:
        return False, "Check-out date must be after check-in date."
    return True, ""


def calculate_days(check_in_str: str, check_out_str: str) -> int:
    """Return the number of nights between two YYYY-MM-DD date strings."""
    ci = parse_date(check_in_str)
    co = parse_date(check_out_str)
    return (co - ci).days


def validate_price(price_str: str) -> bool:
    """Return True if price_str is a positive float."""
    try:
        return float(price_str) > 0
    except ValueError:
        return False


def validate_room_number(room_number: str) -> bool:
    """Room number must be 1–10 alphanumeric characters."""
    return bool(re.fullmatch(r"[A-Za-z0-9\-]{1,10}", room_number.strip()))


# ---------------------------------------------------------------------------
# Secure input helpers
# ---------------------------------------------------------------------------

def get_password_input(prompt: str = "Password: ") -> str:
    """Read a password without echoing characters (cross-platform)."""
    try:
        import getpass
        return getpass.getpass(prompt)
    except Exception:
        # Fallback for environments where getpass doesn't work
        return input(prompt)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def print_separator(char: str = "─", width: int = 56) -> None:
    print(f"{Colors.DIM}{char * width}{Colors.RESET}")


def print_table_header(columns: list, widths: list) -> None:
    """Print a table header row with column names."""
    header = "  ".join(str(col).ljust(w) for col, w in zip(columns, widths))
    print(f"{Colors.LABEL}{Style.BRIGHT}{header}{Style.RESET_ALL}")
    print_separator()


def print_table_row(values: list, widths: list, color: str = "") -> None:
    """Print a single table data row."""
    row = "  ".join(str(v).ljust(w) for v, w in zip(values, widths))
    print(f"{color}{row}{Style.RESET_ALL}")


def format_currency(amount: float) -> str:
    """Return a ₹-formatted currency string."""
    return f"₹{amount:,.2f}"


def press_enter_to_continue() -> None:
    """Pause execution until the user presses Enter."""
    input(f"\n{Colors.DIM}  Press Enter to continue...{Colors.RESET}")


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def prompt(label: str, default: str = "") -> str:
    """
    Display a styled prompt and return stripped user input.
    Shows the default value in brackets if provided.
    """
    if default:
        display = f"{Colors.LABEL}  {label} [{default}]: {Colors.RESET}"
    else:
        display = f"{Colors.LABEL}  {label}: {Colors.RESET}"
    value = input(display).strip()
    return value if value else default


def prompt_int(label: str, min_val: int = None, max_val: int = None) -> int:
    """
    Repeatedly prompt until an integer within [min_val, max_val] is entered.
    Raises KeyboardInterrupt if the user presses Ctrl+C.
    """
    while True:
        raw = prompt(label)
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                Colors.print_warning(f"Value must be ≥ {min_val}.")
                continue
            if max_val is not None and val > max_val:
                Colors.print_warning(f"Value must be ≤ {max_val}.")
                continue
            return val
        except ValueError:
            Colors.print_error("Please enter a valid integer.")


def prompt_float(label: str, min_val: float = 0.0) -> float:
    """Repeatedly prompt until a float ≥ min_val is entered."""
    while True:
        raw = prompt(label)
        try:
            val = float(raw)
            if val < min_val:
                Colors.print_warning(f"Value must be ≥ {min_val}.")
                continue
            return val
        except ValueError:
            Colors.print_error("Please enter a valid number.")
