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
        placeable_coords = []

        # find all coords where player can place a tile
        for coord in self.board.blank_coords():
            if self.board.adjacent_to_player(coord, self.color):
                placeable_coords.append(coord)

        all_pieces = all_permutations()
        valid_placements = set()

        # find all valid moves
        for coord in placeable_coords:
            for piece in all_pieces:
                # try to play the piece with each 4 of its squares on the valid coord
                for i in range(4):
                    moved_piece = piece.make_centre(i).move_to_coord(coord).coords
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
        queue.put((evaluate(node.board, color), node))

    return queue.get()[1].placement
