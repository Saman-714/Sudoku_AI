from __future__ import annotations

from time import perf_counter

from csp import is_valid


def solve(board: list[int]) -> dict:
    if len(board) != 81:
        raise ValueError("board must contain exactly 81 cells")
    work = board[:]
    states = backtracks = 0

    def dfs(pos: int = 0) -> bool:
        nonlocal states, backtracks
        while pos < 81 and work[pos] != 0:
            pos += 1
        if pos == 81:
            return True
        for value in range(1, 10):
            states += 1
            if is_valid(work, pos, value):
                work[pos] = value
                if dfs(pos + 1):
                    return True
                work[pos] = 0
                backtracks += 1
        return False

    start = perf_counter()
    if not dfs():
        raise ValueError("board has no solution")
    return {"solution": work, "states_explored": states, "backtracks": backtracks, "time": perf_counter() - start}