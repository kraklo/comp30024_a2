from referee.game import PlayerColor
from .board_utils import Board
from .node import Node


def evaluate(board: Board, color: PlayerColor) -> float:
    node = Node(None, board, color)
    num_valid_moves = len(node.generate_nodes())

    return num_valid_moves
