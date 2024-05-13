import gc
import random
from typing import Optional, List

from .board_utils import Board
from .tetromino import TetrominoShape
from referee.game import PlaceAction, PlayerColor, Coord


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

    def generate_nodes(self, pieces: List[TetrominoShape]) -> List['Node']:
        valid_placements = set()
        blank_coords = self.board.blank_coords()

        for piece in pieces:
            for coord in blank_coords:
                moved_piece = piece.move_to_coord(coord).coords
                placement = PlaceAction(moved_piece[0], moved_piece[1], moved_piece[2], moved_piece[3])

                if self.board.is_place_valid(placement, self.color):
                    valid_placements.add(placement)
                else:
                    del placement

                del moved_piece

        nodes = []

        for placement in valid_placements:
            nodes.append(self.play_move(placement))

        del blank_coords
        gc.collect()
        return nodes

    def random_move(self, pieces: List[TetrominoShape], coords: List[Coord]) -> Optional['Node']:
        pieces_len = len(pieces)
        coords_len = len(coords)
        piece_index = random.randint(0, pieces_len - 1)
        coord_index = random.randint(0, coords_len - 1)
        piece_count = 0
        coord_count = 0

        while piece_count < pieces_len:
            piece = pieces[piece_index]

            while coord_count < coords_len:
                coord = coords[coord_index]
                moved_piece = piece.move_to_coord(coord).coords
                placement = PlaceAction(moved_piece[0], moved_piece[1], moved_piece[2], moved_piece[3])

                if self.board.is_place_valid(placement, self.color):
                    new_move = self.play_move(placement)
                    del self
                    return new_move

                coord_index = coord_index + 1 if coord_index != coords_len - 1 else 0
                coord_count += 1

            piece_index = piece_index + 1 if piece_index != pieces_len - 1 else 0
            piece_count += 1

        del self
        return None

    # random playout from a given node, returns if this node won
    def playout(self, pieces: List[TetrominoShape]) -> PlayerColor:
        random.shuffle(pieces)
        coords = self.board.blank_coords()
        random.shuffle(coords)
        node = self
        random_move = node.random_move(pieces, coords)

        while random_move:
            node = random_move
            random_move = random_move.random_move(pieces, coords)

        del coords
        return node.color
