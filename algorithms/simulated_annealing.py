from __future__ import annotations

import math
import random
from time import perf_counter


def solve(board: list[int]) -> dict:
    if len(board) != 81:
        raise ValueError("board must contain exactly 81 cells")
    fixed = {i for i, v in enumerate(board) if v != 0}
    work = board[:]
    for box in range(9):
        cells = [r * 9 + c for r in range((box // 3) * 3, (box // 3) * 3 + 3) for c in range((box % 3) * 3, (box % 3) * 3 + 3)]
        empties = [cell for cell in cells if cell not in fixed]
        nums = [n for n in range(1, 10) if n not in {work[cell] for cell in cells if work[cell]}]
        random.shuffle(nums)
        for i, cell in enumerate(empties): work[cell] = nums[i] if i < len(nums) else random.randint(1, 9)

    def cost(b: list[int]) -> int:
        return sum(9 - len({b[r * 9 + c] for c in range(9)}) for r in range(9)) + sum(9 - len({b[r * 9 + c] for r in range(9)}) for c in range(9))

    def box_cells(box: int) -> list[int]:
        br, bc = (box // 3) * 3, (box % 3) * 3
        return [r * 9 + c for r in range(br, br + 3) for c in range(bc, bc + 3) if r * 9 + c not in fixed]

    states = backtracks = 0
    start = perf_counter()
    curr = cost(work)
    temp = 1.0
    for _ in range(100000):
        if curr == 0:
            break
        box = random.randrange(9)
        cells = box_cells(box)
        if len(cells) < 2:
            temp *= 0.9999
            continue
        a, b = random.sample(cells, 2)
        work[a], work[b] = work[b], work[a]
        nxt = cost(work)
        delta = nxt - curr
        accept = delta <= 0 or random.random() < math.exp(-delta / temp)
        states += 1
        if accept:
            curr = nxt
        else:
            work[a], work[b] = work[b], work[a]
            backtracks += 1
        temp *= 0.9999
    return {"solution": work, "states_explored": states, "backtracks": backtracks, "time": perf_counter() - start, "solved": curr == 0}