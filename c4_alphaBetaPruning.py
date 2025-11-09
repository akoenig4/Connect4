import copy
from c4_gameLogic import (
    value, isHumTurn, isFinished, getNext
)

"""
Alpha-Beta Pruning for Connect 4

This module implements the alpha-beta pruning algorithm for finding the best move
in a Connect 4 game. It uses the heuristic evaluation function from connect4.py
to score board positions.

The algorithm works by:
1. Recursively exploring the game tree to a specified depth
2. Using alpha and beta bounds to prune branches that won't affect the final decision
3. Returning both the best value and the resulting state after the best move
"""

def go(s, depth):
    """
    Entry point for alpha-beta pruning.
    Determines whose turn it is and calls the appropriate function.
    
    Args:
        s: Current game state [board, heuristic_value, whose_turn, empty_cells]
        depth: How deep to search in the game tree
    
    Returns:
        The best state to move to (after making the best move)
    """
    if isHumTurn(s):
        # Human is MAX (trying to minimize computer's score / maximize their own)
        result = abmin(s, depth, float("-inf"), float("inf"))
    else:
        # Computer is MAX (trying to maximize score)
        result = abmax(s, depth, float("-inf"), float("inf"))

    best_state, best_col = result[1]
    
    return best_state, best_col  # Return the best state and the column that was added to


def abmax(s, d, a, b):
    """
    Alpha-Beta pruning for MAX player (Computer).
    MAX wants to MAXIMIZE the score.
    
    Args:
        s: Current game state
        d: Current depth (0 when we should stop searching)
        a: Alpha - best value MAX has found so far
        b: Beta - best value MIN can force so far
    
    Returns:
        [value, best_state]: The heuristic value and the state after the best move
    """
    # BASE CASE: Stop if we've reached max depth or game is finished
    v = value(s)
    if d == 0 or isFinished(s):
        return [v, None]
    
    # RECURSIVE CASE: Explore all possible moves
    v = float("-inf")
    best_move = None
    next_states = getNext(s)

    # Move ordering
    next_states.sort(key=lambda x: value(x[0]), reverse=True)
    
    for child_state, col in next_states:
        # Recursively call MIN (opponent's turn)
        tmp = abmin(copy.deepcopy(child_state), d - 1, a, b)
        
        # If this move is better for MAX, update best move and value
        if tmp[0] > v:
            v = tmp[0]
            best_move = child_state, col
        
        # PRUNING: If we found something >= beta, MIN won't let us get here
        # (MIN would choose a different branch at the parent level)
        if v >= b:
            return [v, best_move]
        
        # Update alpha (our guarantee)
        if v > a:
            a = v
    
    return [v, best_move]


def abmin(s, d, a, b):
    """
    Alpha-Beta pruning for MIN player (Human).
    MIN wants to MINIMIZE the score.
    
    Args:
        s: Current game state
        d: Current depth (0 when we should stop searching)
        a: Alpha - best value MAX can force so far
        b: Beta - best value MIN has found so far
    
    Returns:
        [value, best_state]: The heuristic value and the state after the best move
    """
    # BASE CASE: Stop if we've reached max depth or game is finished
    v = value(s)
    if d == 0 or isFinished(s):
        return [v, None]
    
    # RECURSIVE CASE: Explore all possible moves
    v = float("inf")
    best_move = None
    next_states = getNext(s)

    # Move ordering
    next_states.sort(key=lambda x: value(x[0]))
    
    for child_state, col in next_states:
        # Recursively call MAX (our turn)
        tmp = abmax(copy.deepcopy(child_state), d - 1, a, b)
        
        # If this move is better for MIN, update best move and value
        if tmp[0] < v:
            v = tmp[0]
            best_move = child_state, col
        
        # PRUNING: If we found something <= alpha, MAX won't let us get here
        # (MAX would choose a different branch at the parent level)
        if v <= a:
            return [v, best_move]
        
        # Update beta (our guarantee)
        if v < b:
            b = v
    
    return [v, best_move]