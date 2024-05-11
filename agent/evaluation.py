from .board_utils import Board
from referee.game import PlayerColor


def evaluate(board: Board, color) -> int:
    val = 0
    val = board.number_of_player_blocks(color)

    return val
