from termcolor import colored
import c4_alphaBetaPruning as abp
from c4_gameLogic import create, print_board, is_valid_location, makeMove, isHumTurn, isComputerTurn, print_board_after_turn, game_is_won, get_valid_locations
from c4_constants import (
    RED_INT, BLUE_INT,
)


if __name__ == "__main__":
    SEARCH_DEPTH = 5
    state = create()  # Get the starting state
    board = state[0]
    print_board(board)
    game_over = False
    
    while not game_over:
        if isHumTurn(state) and not game_over: # Human's turn
            col = int(input(colored("RED please choose a column(1-7): ", 'red')))
            while col > 7 or col < 1:
                col = int(input("Invalid column, pick a valid one: "))
            while not is_valid_location(board, col - 1):
                col = int(input("Column is full. pick another one..."))
            col -= 1
    
            makeMove(state, col)
            board = state[0] # Update board after human move
            print_board_after_turn(board, col)
    
        if isComputerTurn(state
        ) and not game_over: # Agent's turn
            print(colored("BLUE is making a move...", 'blue'))
            # record time for performance measurement if needed
            import time
            start = time.time()  
            state, col = abp.go(state, SEARCH_DEPTH)
            # result will be the best state after agent's move
            board = state[0]
            end = time.time()
            print(f"BLUE played in {end - start:.4f} seconds. DEPTH = {SEARCH_DEPTH}")
            print_board_after_turn(board, col)
    
        
        
        # Check for win/draw
        if game_is_won(board, RED_INT):
            game_over = True
            print(colored("Red wins!", 'red'))
        if game_is_won(board, BLUE_INT):
            game_over = True
            print(colored("Blue wins!", 'blue'))
        if len(get_valid_locations(board)) == 0:
            game_over = True
            print(colored("Draw!", 'green'))