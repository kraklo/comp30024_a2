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

        if self.color == PlayerColor.RED:
            color = PlayerColor.BLUE
        else:
            color = PlayerColor.RED

        return Node(placement, new_board, color)

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

    def random_move(self) -> Optional['Node']:
        all_pieces = all_permutations()
        random.shuffle(all_pieces)
        blank_coords = self.board.blank_coords()
        random.shuffle(all_pieces)

        for piece in all_pieces:
            for coord in blank_coords:
                moved_piece = piece.move_to_coord(coord).coords
                placement = PlaceAction(moved_piece[0], moved_piece[1], moved_piece[2], moved_piece[3])

                if self.board.is_place_valid(placement, self.color):
                    return self.play_move(placement)

        return None

    # random playout from a given node, returns if this node won
    def playout(self) -> PlayerColor:
        node = self
        random_move = node.random_move()

        while random_move:
            node = random_move
            random_move = random_move.random_move()

        return node.color
