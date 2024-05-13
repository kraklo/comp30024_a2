import copy
import gc
from typing import List

from referee.game import PlaceAction
from referee.game.coord import Coord
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N


class Board:
    def __init__(self, board: dict):
        self.board = board
        self.board_string = self.board_to_string()

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
            flag = False
            if self.board.get(coord, None) is not None and self.board[coord] == color:
                flag = True

            del coord
            if flag:
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
            if self.board.get(coord, None) is not None:
                return False

            if not is_adjacent and self.adjacent_to_player(coord, color):
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

        del self.board
        del self.board_string
        del full_rows
        del full_cols
        self.board = new_board
        self.board_string = self.board_to_string()
        gc.collect()

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

                del this_coord

        gc.collect()
        return player_blocks

    def board_to_string(self) -> str:
        board = ''

        for i in range(BOARD_N):
            for j in range(BOARD_N):
                coord = Coord(i, j)
                if coord not in self.board.keys():
                    board += '_'
                    continue

                board += 'r' if self.board[coord] == PlayerColor.RED else 'b'
                del coord

        gc.collect()
        return board
