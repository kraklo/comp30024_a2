import copy
from typing import List

from referee.game import PlaceAction
from referee.game.coord import Coord
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N


class Board:
    def __init__(self, board: dict):
        self.board = board
        self.board_string = self.board_to_string()
        print(self.board_string)

    # return all blank coords
    def blank_coords(self):
        coords = []

        for r in range(BOARD_N):
            for c in range(BOARD_N):
                this_coord = Coord(r, c)

                if this_coord not in self.board.keys():
                    coords.append(this_coord)

        return coords

    # returns true if this coord is next to the player's square
    def adjacent_to_player(self, coord: Coord, color: PlayerColor) -> bool:
        adjacent_coords = (coord.up(), coord.down(), coord.left(), coord.right())

        for coord in adjacent_coords:
            if coord in self.board.keys() and self.board[coord] == color:
                return True

        return False

    def is_first_turn(self, color: PlayerColor) -> bool:
        for coord in self.board.keys():
            if self.board[coord] == color:
                return False

        return True

    # returns true if a placement is valid
    def is_place_valid(self, place: PlaceAction, color: PlayerColor) -> bool:
        is_adjacent = False

        for coord in place.coords:
            # not a valid placement if there is already a square here
            if coord in self.board.keys():
                return False

            if self.adjacent_to_player(coord, color) or self.is_first_turn(color):
                is_adjacent = True

        return is_adjacent

    def clear_full_lines(self) -> None:
        full_rows = []
        full_cols = []
        keys = self.board.keys()

        # get full rows
        for i in range(BOARD_N):
            row_full = True

            for j in range(BOARD_N):
                if Coord(i, j) not in keys:
                    row_full = False
                    break

            if row_full:
                full_rows.append(i)

        # get full columns
        for i in range(BOARD_N):
            col_full = True

            for j in range(BOARD_N):
                if Coord(j, i) not in keys:
                    col_full = False
                    break

            if col_full:
                full_cols.append(i)

        # create new board without full rows and columns
        new_board = {}

        for coord in keys:
            if coord.r not in full_rows and coord.c not in full_cols:
                new_board[coord] = self.board[coord]

        self.board = new_board
        self.board_string = self.board_to_string()

    def play_move(self, placement: PlaceAction, color: PlayerColor) -> 'Board':
        new_board = copy.deepcopy(self)
        for coord in placement.coords:
            new_board.board[coord] = color

        new_board.clear_full_lines()

        return new_board

    def number_of_player_blocks(self, color) -> int:
        player_blocks = 0
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                this_coord = Coord(r, c)
                if this_coord in self.board.keys() and self.board[this_coord] == color:
                    player_blocks += 1

        return player_blocks

    # test method for more efficiently generating moves (current tests show it's slower)
    def playable_squares(self) -> List[Coord]:
        visited_squares_matrix = [[False] * BOARD_N for i in range(BOARD_N)]
        playable_squares = []
        blank_coords = self.blank_coords()

        for coord in blank_coords:
            if visited_squares_matrix[coord.r][coord.c]:
                continue

            path = [coord]
            visited_squares = [coord]
            visited_squares_matrix[coord.r][coord.c] = True
            path_length = 0

            while len(path) != 0:
                path_coord = path.pop()
                path_length += 1

                adjacent_coords = (path_coord.up(), path_coord.down(), path_coord.left(), path_coord.right())

                for adj_coord in adjacent_coords:
                    if not visited_squares_matrix[adj_coord.r][adj_coord.c] and adj_coord in blank_coords:
                        visited_squares.append(adj_coord)
                        visited_squares_matrix[adj_coord.r][adj_coord.c] = True
                        path.append(adj_coord)

            if path_length >= 4:
                for square in visited_squares:
                    playable_squares.append(square)

        return playable_squares

    def board_to_string(self) -> str:
        board = ''

        for i in range(BOARD_N):
            for j in range(BOARD_N):
                coord = Coord(i, j)
                if coord not in self.board.keys():
                    board += '_'
                    continue

                board += 'r' if self.board[coord] == PlayerColor.RED else 'b'

        return board

    def is_transposition(self, other: 'Board') -> bool:
        return other.board_string in (self.board_string + self.board_string)
