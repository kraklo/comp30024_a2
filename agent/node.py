import random
from typing import Optional, List

from .board_utils import Board
from .tetromino import all_permutations
from referee.game import PlaceAction, PlayerColor


class Node:
    def __init__(self, placement: Optional[PlaceAction], board: Board, color: PlayerColor):
        self.placement = placement
        self.board = board
        self.color = color

    def __lt__(self, other):
        return random.choice((True, False))

    def play_move(self, placement: PlaceAction) -> 'Node':
        new_board = self.board.play_move(placement, self.color)

        return Node(placement, new_board, self.color)

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
