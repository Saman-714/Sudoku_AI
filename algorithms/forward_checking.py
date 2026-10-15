from __future__ import annotations

from time import perf_counter
from csp import get_peers, is_valid


def solve(board: list[int]) -> dict:
    if len(board) != 81:
        raise ValueError("board must contain exactly 81 cells")
    if any(board[i] and not is_valid(board, i, board[i]) for i in range(81)):
        raise ValueError("board has no solution")
    work = board[:]
    domains = {i: ({board[i]} if board[i] else {v for v in range(1, 10) if is_valid(board, i, v)}) for i in range(81)}
    states = backtracks = 0

    def dfs() -> bool:
        nonlocal states, backtracks
        cell = next((i for i in range(81) if work[i] == 0), None)
        if cell is None:
            return True
        for v in sorted(domains[cell]):
            states += 1
            if is_valid(work, cell, v):
                saved = {i: domains[i].copy() for i in get_peers(cell) | {cell}}
                work[cell] = v
                domains[cell] = {v}
                ok = True
                for peer in get_peers(cell):
                    if work[peer] == 0:
                        domains[peer].discard(v)
                        if not domains[peer]: ok = False; break
                if ok and dfs():
                    return True
                work[cell] = 0
                for i, d in saved.items(): domains[i] = d
                backtracks += 1
        return False

    start = perf_counter()
    if not dfs():
        raise ValueError("board has no solution")
    return {"solution": work, "states_explored": states, "backtracks": backtracks, "time": perf_counter() - start}