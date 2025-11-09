import copy
import sys
import numpy as np
import random
from termcolor import colored  # can be taken out if you don't like it...
from c4_constants import (
    ROW_COUNT, COLUMN_COUNT,
    RED_CHAR, BLUE_CHAR,
    NEW_RED_CHAR, NEW_BLUE_CHAR,
    VIC, LOSS, TIE,
    COMPUTER, HUMAN
)


# # # # # # # # # # # # # # BOARD FUNCTIONS # # # # # # # # # # # # # #

def create_board():
    """Create empty board for new game"""
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
    return board


def drop_chip(board, row, col, chip):
    """Place a chip (red or blue) in a certain position in board"""
    board[row][col] = chip


def is_valid_location(board, col):
    """Check if a given column has room for an extra dropped chip"""
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    """Assuming column is available, return the lowest empty row"""
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
    return -1  # Column is full


def print_board(board):
    """Print current board with all chips placed so far"""
    print(" 1 2 3 4 5 6 7 \n" "|" + np.array2string(np.flip(np.flip(board, 1)))
          .replace("[", "").replace("]", "").replace(" ", "|").replace("0", "_")
          .replace("1", RED_CHAR).replace("2", BLUE_CHAR).replace("\n", "|\n") + "|")

def print_board_after_turn(board, new_col):
    """Print board after a turn, highlighting the newly placed chip"""
    for r in range(ROW_COUNT):
        if board[r][new_col] != 0:
            new_row = r
    print(" 1 2 3 4 5 6 7 ")
    for r in reversed(range(len(board))):
        print("|", end="")
        for c in range(len(board[0])):
            val = board[r][c]
            if r == new_row and c == new_col:
                if val == 1:
                    print(NEW_RED_CHAR, end="|")
                elif val == 2:
                    print(NEW_BLUE_CHAR, end="|")
            else:
                if val == 0:
                    print("_", end="|")
                elif val == 1:
                    print(RED_CHAR, end="|")
                elif val == 2:
                    print(BLUE_CHAR, end="|")
        print()

def game_is_won(board, chip):
    """Check if board contains a sequence of 4-in-a-row for given chip"""
    winning_Sequence = np.array([chip, chip, chip, chip])
    
    # Check horizontal sequences
    for r in range(ROW_COUNT):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[r, :]))):
            return True
    
    # Check vertical sequences
    for c in range(COLUMN_COUNT):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[:, c]))):
            return True
    
    # Check positively sloped diagonals
    for offset in range(-2, 4):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board.diagonal(offset)))):
            return True
    
    # Check negatively sloped diagonals
    for offset in range(-2, 4):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, np.flip(board, 1).diagonal(offset)))):
            return True
    
    return False


def get_valid_locations(board):
    """Return list of valid columns to play in"""
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def MoveRandom(board, color):
    """Make a random move"""
    valid_locations = get_valid_locations(board)
    column = random.choice(valid_locations)
    row = get_next_open_row(board, column)
    drop_chip(board, row, column, color)


# # # # # # # # # # # # # # GAME STATE FUNCTIONS (for alpha-beta) # # # # # # # # # # # # # #

"""
State representation for alpha-beta:
[board, heuristic_value, whose_turn, empty_cells]
  - board: 6x7 numpy array with 0 (empty), 1 (red/human), 2 (blue/computer)
  - heuristic_value: score of the position
  - whose_turn: HUMAN or COMPUTER
  - empty_cells: number of empty cells remaining
"""

def create():
    """Returns an empty game state. Asks who plays first."""
    board = create_board()
    state = [board, 0.00001, HUMAN, ROW_COUNT * COLUMN_COUNT]

    # Automatically detect if we're inside Streamlit
    running_in_streamlit = "streamlit" in sys.modules
    whoIsFirst(state, streamlit_ui=running_in_streamlit)
    return state


def value(s):
    """Returns the heuristic value of state s"""
    return s[1]


def printState(s):
    """Print the board state"""
    print_board(s[0])
    if value(s) == VIC:
        print(colored("Computer wins!", 'blue'))
    elif value(s) == LOSS:
        print(colored("Human wins!", 'red'))
    elif value(s) == TIE:
        print("It's a tie!")


def isFinished(s):
    """Returns True if the game ended"""
    return s[1] in [LOSS, VIC, TIE]


def isHumTurn(s):
    """Returns True if it's the human's turn"""
    return s[2] == HUMAN


def isComputerTurn(s):
    """Returns True if it's the computer's turn"""
    return s[2] == COMPUTER


def whoIsFirst(s, streamlit_ui=False):
    """Let user decide who plays first."""
    if streamlit_ui:
        import streamlit as st
        choice = st.radio("Who plays first?", ["You (Red)", "Computer (Blue)"])
        s[2] = COMPUTER if choice == "Computer (Blue)" else HUMAN
    else:
        choice = input("Who plays first? 1-computer / anything else-you: ")
        s[2] = COMPUTER if choice == "1" else HUMAN


def makeMove(s, col):
    """
    Drop a chip in column col for the current player.
    Updates: board state, whose turn, heuristic value, empty cell count.
    Assumes move is legal (column is not full).
    """
    # Find lowest empty row in this column
    row = get_next_open_row(s[0], col)
    if row == -1:
        return  # Column full, shouldn't happen
    
    # Drop the chip
    drop_chip(s[0], row, col, s[2])
    s[3] -= 1  # Decrement empty cells
    s[2] = COMPUTER + HUMAN - s[2]  # Switch turns
    
    # Re-evaluate board
    evaluateBoard(s)


def evaluateBoard(s):
    """
    Evaluate the heuristic value of the board.
    Checks for wins/losses first, then counts threats and patterns.
    """
    board = s[0]
    
    # Check for immediate win/loss
    if game_is_won(board, COMPUTER):
        s[1] = VIC
        return
    if game_is_won(board, HUMAN):
        s[1] = LOSS
        return
    
    # Check for tie
    if s[3] == 0:
        s[1] = TIE
        return
    
    # Count threats and positional advantages
    s[1] = countThreats(board)


def countThreats(board):
    """
    Count potential winning sequences for both players.
    Adds positional and double-trap heuristics.
    Returns: positive score if computer is favored, negative if human is favored.
    """
    score = 0.00001
    double_trap_computer = 0
    double_trap_human = 0
    
    # --- Center column control (strategic advantage) ---
    center_col_index = COLUMN_COUNT // 2
    center_col = [board[r][center_col_index] for r in range(ROW_COUNT)]
    score += center_col.count(COMPUTER) * 3
    score -= center_col.count(HUMAN) * 3

    # --- Check all directions: horizontal, vertical, and both diagonals ---
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    # Track how many "open 3s" each player has for double trap detection
    comp_threats = 0
    human_threats = 0
    
    # -- Determine value of each 4-cell sequence ---
    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT):
            for dr, dc in directions:
                threat = checkSequence(board, row, col, dr, dc)
                score += threat[0]
                if threat[1] == "COMP_THREAT":
                    comp_threats += 1
                elif threat[1] == "HUM_THREAT":
                    human_threats += 1

    # --- Double trap detection ---
    if comp_threats >= 2:
        score += 500000  # Strong positional fork
    if human_threats >= 2:
        score -= 500000  # Opponent fork is very bad

    return score


def checkSequence(board, start_row, start_col, dr, dc):
    """
    Evaluate a 4-cell window starting at (start_row, start_col)
    going in direction (dr, dc).
    Returns (score_delta, threat_flag).
    """
    end_row = start_row + 3 * dr
    end_col = start_col + 3 * dc
    
    # Out of bounds
    if end_row < 0 or end_row >= ROW_COUNT or end_col < 0 or end_col >= COLUMN_COUNT:
        return (0, None)
    
    window = [board[start_row + i * dr][start_col + i * dc] for i in range(4)]
    
    computer_count = window.count(COMPUTER)
    human_count = window.count(HUMAN)
    empty_count = window.count(0)
    
    # Blocked window (both players present)
    if computer_count > 0 and human_count > 0:
        return (0, None)

    score = 0
    threat_flag = None

    # --- Scoring ---
    if computer_count == 4:
        score += 1000000  # Win is ultimate goal
    elif human_count == 4:
        score -= 1000000
    elif computer_count == 3 and empty_count == 1:
        score += 100000   # Near-win is next best
        threat_flag = "COMP_THREAT"
    elif human_count == 3 and empty_count == 1:
        score -= 100000   
        threat_flag = "HUM_THREAT"
    elif computer_count == 2 and empty_count == 2:
        score += 100      # 2 with 2 empty is good
    elif human_count == 2 and empty_count == 2:
        score -= 100      
    elif computer_count == 1 and empty_count == 3:
        score += 10     # 1 with 3 empty is okay
    elif human_count == 1 and empty_count == 3:
        score -= 10

    return (score, threat_flag)


def isValidMove(s, col):
    """Check if column is valid and not full"""
    if col < 0 or col >= COLUMN_COUNT:
        return False
    return is_valid_location(s[0], col)


def getValidMoves(s):
    """Returns list of valid columns to play in"""
    return get_valid_locations(s[0])


def getNext(s):
    """
    Returns a list of all possible next states.
    Each state is a deep copy with one valid move applied.
    """
    next_states = []
    
    for col in getValidMoves(s):
        tmp = copy.deepcopy(s)
        makeMove(tmp, col)
        next_states.append((tmp, col))
    
    return next_states


def inputMove(s):
    """Read and execute the human player's move"""
    printState(s)
    flag = True
    while flag:
        try:
            col = int(input(f"{['BLUE', 'RED'][s[2]-1]} please choose a column(1-7): ")) - 1
            if col < 0 or col >= COLUMN_COUNT:
                print("Invalid column, pick a valid one (1-7):")
            elif not is_valid_location(s[0], col):
                print("Column is full. Pick another one...")
            else:
                flag = False
                makeMove(s, col)
        except ValueError:
            print("Please enter a number between 1 and 7.")