from termcolor import colored

# # # # # # # # # # # # # # global values  # # # # # # # # # # # # # #
ROW_COUNT = 6
COLUMN_COUNT = 7

RED_CHAR = colored('X', 'red')  # RED_CHAR = 'X'
BLUE_CHAR = colored('O', 'blue')  # BLUE_CHAR = 'O'

NEW_RED_CHAR = colored('X', 'red', attrs=["bold"])
NEW_BLUE_CHAR = colored('O', 'blue', attrs=["bold"])

EMPTY = 0
RED_INT = 1
BLUE_INT = 2

# Game constants for alpha-beta
VIC = 10**20              # Value of a winning board (for MAX/agent)
LOSS = -VIC               # Value of a losing board (for MAX/agent)
TIE = 0                   # Value of a tie

COMPUTER = BLUE_INT       # Agent plays as BLUE
HUMAN = RED_INT           # Human plays as RED
