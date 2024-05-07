from enum import Enum
from typing import List

from referee.game.coord import Coord, Vector2


class TetrominoShape:
    def __init__(self, coords: List[Vector2]):
        self.coords = coords

    # move the piece so all coords are positive
    def make_positive(self) -> None:
        min_r = 0
        min_c = 0

        for coord in self.coords:
            if coord.c < min_c:
                min_c = coord.c

            if coord.r < min_r:
                min_r = coord.r

        for i in range(len(self.coords)):
            new_coord = self.coords[i].down(-min_r)
            new_coord = new_coord.right(-min_c)

            # switch back to coords as these will be Vector2
            self.coords[i] = Coord(new_coord.r, new_coord.c)

    # rotate a piece 90 degrees clockwise rotations times
    def rotate(self, rotations: int) -> 'TetrominoShape':
        new_coords = []

        # rotate each point 90deg around origin
        for coord in self.coords:
            # have to use Vector2 as coords will briefly be out of bounds
            new_coords.append(Vector2(coord.c, -coord.r))

        new_shape = TetrominoShape(new_coords)
        new_shape.make_positive()

        # use recursion to rotate multiple times
        if rotations == 1:
            return new_shape

        return new_shape.rotate(rotations - 1)

    # transform piece so that (0, 0) is located at new_coord
    def move_to_coord(self, new_coord):
        new_coords = []
        for coord in self.coords:
            new_coords.append(coord + new_coord)

        return TetrominoShape(new_coords)

    # transform piece so that the coord at coord_index is located at the origin
    def make_centre(self, coord_index):
        new_coords = []
        for coord in self.coords:
            new_coords.append(coord - self.coords[coord_index])

        return TetrominoShape(new_coords)


class Tetromino(Enum):
    LINE = (TetrominoShape([Coord(0, 0), Coord(0, 1), Coord(0, 2), Coord(0, 3)]), 2)
    J = (TetrominoShape([Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(1, 2)]), 4)
    L = (TetrominoShape([Coord(1, 0), Coord(1, 1), Coord(1, 2), Coord(0, 2)]), 4)
    BOX = (TetrominoShape([Coord(0, 0), Coord(0, 1), Coord(1, 0), Coord(1, 1)]), 0)
    S = (TetrominoShape([Coord(1, 0), Coord(1, 1), Coord(0, 1), Coord(0, 2)]), 2)
    Z = (TetrominoShape([Coord(0, 0), Coord(0, 1), Coord(1, 1), Coord(1, 2)]), 2)
    T = (TetrominoShape([Coord(1, 0), Coord(1, 1), Coord(0, 1), Coord(1, 2)]), 4)


def all_shapes() -> List[Tetromino]:
    return [Tetromino.LINE, Tetromino.J, Tetromino.L, Tetromino.BOX, Tetromino.S, Tetromino.Z, Tetromino.T]


# all tetromino shapes in all rotations
def all_permutations() -> List[TetrominoShape]:
    permutations = []

    for shape in all_shapes():
        permutations.append(shape.value[0])

        # append a single 90 degree rotation if shape is not totally symmetrical
        if shape.value[1] >= 2:
            permutations.append(shape.value[0].rotate(1))

        # append other rotations if shape has no axis of symmetry
        if shape.value[1] == 4:
            permutations.append(shape.value[0].rotate(2))
            permutations.append(shape.value[0].rotate(3))

    return permutations
