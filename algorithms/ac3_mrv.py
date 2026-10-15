from __future__ import annotations

from collections import deque
from time import perf_counter
from csp import get_peers, is_valid


def solve(board: list[int]) -> dict:
    if len(board) != 81:
        raise ValueError("board must contain exactly 81 cells")
    if any(board[i] and not is_valid(board, i, board[i]) for i in range(81)):
        raise ValueError("board has no solution")
    domains = {i: ({board[i]} if board[i] else {v for v in range(1, 10) if is_valid(board, i, v)}) for i in range(81)}
    q = deque((i, j) for i in range(81) for j in get_peers(i))
    while q:
        i, j = q.popleft()
        if len(domains[j]) == 1:
            v = next(iter(domains[j]))
            if v in domains[i] and len(domains[i]) > 1:
                domains[i].remove(v)
                if not domains[i]:
                    raise ValueError("board has no solution")
                q.extend((k, i) for k in get_peers(i) if k != j)
    states = backtracks = 0
    start = perf_counter()

    def dfs() -> bool:
        nonlocal states, backtracks
        cell = min((i for i in range(81) if board[i] == 0), key=lambda i: len(domains[i]), default=None)
        if cell is None:
            return True
        for v in sorted(domains[cell]):
            states += 1
            if is_valid(board, cell, v):
                board[cell] = v
                saved = {k: domains[k].copy() for k in get_peers(cell) | {cell}}
                domains[cell] = {v}
                for k in get_peers(cell):
                    domains[k].discard(v)
                if all(domains[k] for k in range(81)) and dfs():
                    return True
                for k, s in saved.items():
                    domains[k] = s
                board[cell] = 0
                backtracks += 1
        return False

    if not dfs():
        raise ValueError("board has no solution")
    return {"solution": board, "states_explored": states, "backtracks": backtracks, "time": perf_counter() - start}