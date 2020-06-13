from colorama import Fore, Style
import datetime

RED = Fore.RED
WHT = Fore.WHITE
GRN = Fore.GREEN
YEL = Fore.YELLOW

def now():
    """Return current datetime as simple sortable string.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(str, **kwargs):
    """Print STR, reset terminal colors, and return what we printed.
    """
    dt = now()
    # Don't add escape sequences to message for logging purposes.
    # This doesn't remove escape sequences that the caller specified.
    str = f"{now()}: {str}"
    # Print with default color and reset color at the end.
    print(f"{GRN}{str}{Style.RESET_ALL}", **kwargs)
    return str

def log_add(str, **kwargs):
    """Just like log(), but no timestamp or color.
    """
    print(f"{str}{Style.RESET_ALL}", **kwargs)
    return str
