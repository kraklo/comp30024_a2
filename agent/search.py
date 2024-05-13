import random

from referee.game.actions import PlaceAction
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N
from referee.game.coord import Coord

from .node import Node
from .board_utils import Board
from .evaluation import evaluate

MAX_DEPTH = 2


def search(board: Board, color: PlayerColor) -> PlaceAction:
    # set up priority queue
    root = Node(None, board, color)
    moves = []

    if len(board.board.keys()) == 0:
        return PlaceAction(
            Coord(0, 0),
            Coord(0, BOARD_N - 1),
            Coord(BOARD_N - 1, 0),
            Coord(BOARD_N - 1, BOARD_N - 1)
        )
    elif board.is_first_turn(color):
        return PlaceAction(
            Coord(4, 4),
            Coord(4, 5),
            Coord(5, 4),
            Coord(5, 5)
        )

    child_nodes = root.generate_nodes()
    if len(child_nodes) > 0:
        return random.choice(child_nodes).placement

    for node in child_nodes:
        move = (minimax(node, MAX_DEPTH, color), node)
        moves.append(move)

    moves.sort()
    print(moves[0])

    if color == PlayerColor.RED:
        return moves[-1][1].placement

    return moves[0][1].placement


# red is trying to maximise eval while blue is trying to minimise eval
def minimax(node: Node, depth: int, color: PlayerColor, alpha=float('-inf'), beta=float('inf')) -> float:
    child_nodes = node.generate_nodes()

    if len(child_nodes) == 0:
        if color == PlayerColor.RED:
            return float('-inf')

        return float('inf')

    # max depth reached
    if depth == 0:
        return evaluate(node.board, color)

    # maximise eval
    if color == PlayerColor.RED:
        for node in child_nodes:
            alpha = max(alpha, minimax(node, depth - 1, PlayerColor.BLUE, alpha, beta))

            if alpha >= beta:
                return beta

        return alpha
    # minimise eval
    else:
        for node in child_nodes:
            beta = min(beta, minimax(node, depth - 1, PlayerColor.RED, alpha, beta))

            if beta <= alpha:
                return alpha

        return beta
