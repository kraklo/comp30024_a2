import copy

from referee.game.actions import PlaceAction
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N
from referee.game.coord import Coord

from .tetromino import all_permutations
from .board_utils import Board
from queue import PriorityQueue
from .evaluation import evaluate
from typing import Optional, List


class Node:
    def __init__(self, parent: Optional['Node'], placement: Optional[PlaceAction], board: Board, color: PlayerColor):
        self.parent = parent
        self.placement = placement
        self.board = board
        self.color = color
        self.evaluation = evaluate(board, color)

    def __lt__(self, other):
        return self.evaluation < other.evaluation

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
    queue = PriorityQueue()

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
        queue.put((minimax(node.board, 2, float('-inf'), float('inf'), color), node))
        #queue.put((evaluate(node.board, color), node))

    return queue.get()[1].placement


def minimax(board: Board, depth, alpha, beta, color) -> float:
    root = Node(None, None, board, color)
    child_nodes = root.generate_nodes()
    # most desirable to make the other player not able to move
    if len(child_nodes) == 0 and color == PlayerColor.RED:
        return float('inf')
    if len(child_nodes) == 0 and color == PlayerColor.BLUE:
        return float('-inf')

    # max depth reached
    if depth == 0:
        return evaluate(board, color)

    if color == PlayerColor.RED:
        red_max_eval = float('-inf')
        for node in child_nodes:
            red_eval = minimax(node.board, depth - 1, alpha, beta, PlayerColor.BLUE)
            red_max_eval = max(red_max_eval, red_eval)
            alpha = max(alpha, red_eval)
            if beta <= alpha:
                break
            return red_max_eval

    else:
        blue_max_eval = float('inf')
        for node in child_nodes:
            blue_eval = minimax(node.board, depth - 1, alpha, beta, PlayerColor.RED)
            blue_max_eval = min(blue_max_eval, blue_eval)
            beta = min(beta, blue_eval)
            if beta <= alpha:
                break
            return blue_max_eval
