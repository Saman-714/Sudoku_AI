from __future__ import annotations

import random
from typing import List, Optional

from csp import NUM_CELLS, get_peers, is_valid

DIFFICULTY_FILLED_CELLS = {
    "easy": 40,
    "medium": 32,
    "hard": 26,
    "expert": 22,
}


def _find_unassigned_cell(board: List[int]) -> Optional[int]:
    best_cell: Optional[int] = None
    best_count = 10

    for cell, value in enumerate(board):
        if value != 0:
            continue

        candidates = _candidates(board, cell)
        candidate_count = len(candidates)
        if candidate_count == 0:
            return cell
        if candidate_count < best_count:
            best_count = candidate_count
            best_cell = cell
            if candidate_count == 1:
                break

    return best_cell


def _candidates(board: List[int], cell: int) -> List[int]:
    if board[cell] != 0:
        return []

    used = {board[peer] for peer in get_peers(cell) if board[peer] != 0}
    return [value for value in range(1, 10) if value not in used]


def _solve_board(board: List[int], limit: int = 1, randomize: bool = False) -> List[List[int]]:
    solutions: List[List[int]] = []
    working = board[:]

    def backtrack() -> None:
        if len(solutions) >= limit:
            return

        cell = _find_unassigned_cell(working)
        if cell is None:
            solutions.append(working[:])
            return

        values = _candidates(working, cell)
        if randomize:
            random.shuffle(values)

        for value in values:
            if is_valid(working, cell, value):
                working[cell] = value
                backtrack()
                working[cell] = 0
                if len(solutions) >= limit:
                    return

    backtrack()
    return solutions


def get_solution(board: List[int]) -> List[int]:
    if len(board) != NUM_CELLS:
        raise ValueError("board must contain exactly 81 cells")

    solutions = _solve_board(board, limit=1, randomize=False)
    if not solutions:
        raise ValueError("board has no solution")
    return solutions[0]


def _generate_full_solution() -> List[int]:
    board = [0] * NUM_CELLS
    solution = _solve_board(board, limit=1, randomize=True)
    if not solution:
        raise RuntimeError("failed to generate a full Sudoku solution")
    return solution[0]


def _has_unique_solution(board: List[int]) -> bool:
    return len(_solve_board(board, limit=2, randomize=False)) == 1


def generate_puzzle(difficulty: str) -> List[int]:
    if difficulty not in DIFFICULTY_FILLED_CELLS:
        raise ValueError("difficulty must be one of: easy, medium, hard, expert")

    target_filled = DIFFICULTY_FILLED_CELLS[difficulty]
    max_attempts = 100

    for _ in range(max_attempts):
        puzzle = _generate_full_solution()
        cells = list(range(NUM_CELLS))
        random.shuffle(cells)

        for cell in cells:
            if sum(1 for value in puzzle if value != 0) <= target_filled:
                break

            saved_value = puzzle[cell]
            puzzle[cell] = 0

            if not _has_unique_solution(puzzle):
                puzzle[cell] = saved_value

        if sum(1 for value in puzzle if value != 0) == target_filled:
            return puzzle

    raise RuntimeError(f"failed to generate a unique puzzle with {target_filled} filled cells")
