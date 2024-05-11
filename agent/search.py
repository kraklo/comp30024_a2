import random

from referee.game.actions import PlaceAction
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N
from referee.game.coord import Coord

from .tetromino import all_permutations
from .board_utils import Board
from .evaluation import evaluate
from typing import Optional, List

MAX_DEPTH = 0


class Node:
    def __init__(self, parent: Optional['Node'], placement: Optional[PlaceAction], board: Board, color: PlayerColor):
        self.parent = parent
        self.placement = placement
        self.board = board
        self.color = color

    def __lt__(self, other):
        return random.choice((True, False))

    def play_move(self, placement: PlaceAction) -> 'Node':
        new_board = self.board.play_move(placement, self.color)

        return Node(self, placement, new_board, self.color)

    def generate_nodes(self) -> List['Node']:
        all_pieces = all_permutations()
        valid_placements = set()

        for piece in all_pieces:
            for coord in self.board.blank_coords():
                moved_piece = piece.move_to_coord(coord).coords
                placement = PlaceAction(moved_piece[0], moved_piece[1], moved_piece[2], moved_piece[3])

                if self.board.is_place_valid(placement, self.color):
                    valid_placements.add(placement)

        nodes = []

        for placement in valid_placements:
            nodes.append(self.play_move(placement))

        return nodes


def search(board: Board, color: PlayerColor) -> PlaceAction:
    # set up priority queue
    root = Node(None, None, board, color)
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

    for node in child_nodes:
        move = (minimax(node, MAX_DEPTH, color), node)
        moves.append(move)

    child_nodes.sort()

    if color == PlayerColor.RED:
        return child_nodes[-1].placement

    return child_nodes[0].placement


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
