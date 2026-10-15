from __future__ import annotations

from collections import deque
from time import perf_counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from csp import get_peers, is_valid
from algorithms.ac3_mrv import solve as ac3_mrv
from algorithms.backtracking import solve as backtracking
from algorithms.forward_checking import solve as forward_checking
from algorithms.simulated_annealing import solve as simulated_annealing
from puzzle_generator import generate_puzzle, get_solution

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
ALGOS = {"backtracking": backtracking, "ac3_mrv": ac3_mrv, "forward_checking": forward_checking, "simulated_annealing": simulated_annealing}


def _step_solve(board: list[int], algorithm: str):
    work = board[:]
    steps, states, backtracks = [work[:]], 0, 0
    step_every = 10 if algorithm == "backtracking" else 1

    def snap():
        if states % step_every == 0:
            steps.append(work[:])

    def backtrack(pos=0):
        nonlocal states, backtracks
        while pos < 81 and work[pos] != 0:
            pos += 1
        if pos == 81:
            return True
        for v in range(1, 10):
            states += 1
            record = states % step_every == 0
            if is_valid(work, pos, v):
                work[pos] = v
                if backtrack(pos + 1):
                    if record: steps.append(work[:])
                    return True
                work[pos] = 0
                backtracks += 1
            if record: steps.append(work[:])
        return False

    def fc(pos=0, domains=None):
        nonlocal states, backtracks
        if domains is None:
            domains = {i: ({work[i]} if work[i] else {v for v in range(1, 10) if is_valid(work, i, v)}) for i in range(81)}
        cell = next((i for i in range(81) if work[i] == 0), None)
        if cell is None: return True
        for v in sorted(domains[cell]):
            states += 1
            record = states % step_every == 0
            if is_valid(work, cell, v):
                saved = {i: domains[i].copy() for i in get_peers(cell) | {cell}}
                work[cell] = v; domains[cell] = {v}
                ok = True
                for peer in get_peers(cell):
                    if work[peer] == 0:
                        domains[peer].discard(v)
                        ok = ok and bool(domains[peer])
                if ok and fc(cell + 1, domains):
                    if record: steps.append(work[:])
                    return True
                work[cell] = 0; backtracks += 1
                for i, d in saved.items(): domains[i] = d
            if record: steps.append(work[:])
        return False

    def ac3():
        nonlocal states, backtracks
        domains = {i: ({work[i]} if work[i] else {v for v in range(1, 10) if is_valid(work, i, v)}) for i in range(81)}
        q = deque((i, j) for i in range(81) for j in get_peers(i))
        while q:
            i, j = q.popleft()
            if len(domains[j]) == 1:
                v = next(iter(domains[j]))
                if v in domains[i] and len(domains[i]) > 1:
                    domains[i].remove(v)
                    if not domains[i]: return False
                    q.extend((k, i) for k in get_peers(i) if k != j)
        def dfs():
            nonlocal states, backtracks
            cell = min((i for i in range(81) if work[i] == 0), key=lambda i: len(domains[i]), default=None)
            if cell is None: return True
            for v in sorted(domains[cell]):
                states += 1
                record = states % step_every == 0
                if is_valid(work, cell, v):
                    saved = {i: domains[i].copy() for i in get_peers(cell) | {cell}}
                    work[cell] = v; domains[cell] = {v}
                    for peer in get_peers(cell): domains[peer].discard(v)
                    if all(domains[i] for i in range(81)) and dfs():
                        if record: steps.append(work[:])
                        return True
                    work[cell] = 0; backtracks += 1
                    for i, d in saved.items(): domains[i] = d
                if record: steps.append(work[:])
            return False
        return dfs()

    start = perf_counter()
    solved = {"backtracking": backtrack, "forward_checking": fc, "ac3_mrv": ac3}[algorithm]()
    if solved: steps.append(work[:])
    return {"steps": steps, "metrics": {"time": perf_counter() - start, "states_explored": states, "backtracks": backtracks}}


@app.get("/puzzle")
def puzzle(difficulty: str = "easy"):
    board = generate_puzzle(difficulty)
    return {"board": board, "solution": get_solution(board)}


@app.post("/solve")
def solve(payload: dict):
    algo = ALGOS.get(payload.get("algorithm"))
    if not algo:
        raise HTTPException(400, "invalid algorithm")
    return algo(payload.get("board", []))


@app.get("/compare")
def compare(difficulty: str = "easy"):
    puzzle = generate_puzzle(difficulty)
    return {"puzzle": puzzle, "results": {name: fn(puzzle[:]) for name, fn in ALGOS.items()}}


@app.post("/solve/steps")
def solve_steps(payload: dict):
    algorithm = payload.get("algorithm")
    if algorithm not in {"backtracking", "ac3_mrv", "forward_checking"}:
        raise HTTPException(400, "invalid algorithm")
    board = payload.get("board", [])
    if len(board) != 81:
        raise HTTPException(400, "board must contain exactly 81 cells")
    return _step_solve(board, algorithm)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)