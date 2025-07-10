import logging

class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   RESET = '\033[0m'

logger = logging.getLogger("loggerFyTops")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
file_handler = logging.FileHandler(filename="../fytops.log")

console_formatter = logging.Formatter(
    fmt=f"{Color.YELLOW}%(asctime)s {Color.BOLD}{Color.CYAN}%(levelname)s{Color.RESET}\t%(message)s",
    datefmt="%m-%d-%Y %H:%M:%S"
)

file_formatter = logging.Formatter(
    fmt='%(asctime)s %(levelname)s\t[%(message)s] File "%(pathname)s", line %(lineno)d',
    datefmt="%m-%d-%Y %H:%M:%S"
)

console.setLevel("INFO")
console.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

logger.addHandler(console)
logger.addHandler(file_handler)

