from __future__ import annotations

from typing import List, Set

BOARD_SIZE = 9
BOX_SIZE = 3
NUM_CELLS = BOARD_SIZE * BOARD_SIZE


def _to_row_col(cell: int) -> tuple[int, int]:
    return divmod(cell, BOARD_SIZE)


def _to_cell(row: int, col: int) -> int:
    return row * BOARD_SIZE + col


def get_peers(cell: int) -> Set[int]:
    row, col = _to_row_col(cell)
    peers: Set[int] = set()

    for other_col in range(BOARD_SIZE):
        if other_col != col:
            peers.add(_to_cell(row, other_col))

    for other_row in range(BOARD_SIZE):
        if other_row != row:
            peers.add(_to_cell(other_row, col))

    box_row = (row // BOX_SIZE) * BOX_SIZE
    box_col = (col // BOX_SIZE) * BOX_SIZE
    for box_r in range(box_row, box_row + BOX_SIZE):
        for box_c in range(box_col, box_col + BOX_SIZE):
            peer = _to_cell(box_r, box_c)
            if peer != cell:
                peers.add(peer)

    return peers


def is_valid(board: List[int], cell: int, value: int) -> bool:
    if not 0 <= cell < NUM_CELLS:
        return False
    if not 1 <= value <= 9:
        return False
    if board[cell] not in (0, value):
        return False

    for peer in get_peers(cell):
        if board[peer] == value:
            return False

    return True