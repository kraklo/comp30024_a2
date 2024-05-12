from time import time
from typing import List

from referee.game.actions import PlaceAction
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N
from referee.game.coord import Coord

from .node import Node
from .board_utils import Board
from .tetromino import TetrominoShape
from .tree import Tree

MCTS_ITERATIONS = 1000


class TimeStruct:
    def __init__(self):
        self.shuffle = 0
        self.find_valid = 0


def search(board: Board, color: PlayerColor, tree: Tree, pieces: List[TetrominoShape], time_remaining) -> PlaceAction:
    time_struct = TimeStruct()

    if not time_remaining:
        time_remaining = 180

    print(f'time remaining: {time_remaining}')

    turn_start_time = time()
    root = Node(None, board, color)
    root_tree_node = tree.get_node_from_board(board)

    if not root_tree_node:
        root_tree_node = tree.add_tree_node(root, None)

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

    total_select_time = 0
    total_playout_time = 0
    simulation_start_time = time()
    # simulate playouts
    for i in range(MCTS_ITERATIONS):
        if time() - turn_start_time >= min(9.0, time_remaining / 6):
            print(f'out of time! iterations ran: {i}')
            break

        select_start_time = time()

        # select a node
        tree_node = root_tree_node.select_max_child(pieces)

        if not tree_node:
            total_select_time += time() - select_start_time
            break

        while tree_node.playouts != 0:
            new_tree_node = tree_node.select_max_child(pieces)
            if not new_tree_node:
                break

            tree_node = new_tree_node

        total_select_time += time() - select_start_time
        playout_start_time = time()

        # playout
        tree_node.playout(pieces, time_struct)

        total_playout_time += time() - playout_start_time

    simulation_time = time() - simulation_start_time

    print("picking best move")
    curr_time = time()
    # pick the best move
    best_move = root_tree_node.select_best_move()
    print(best_move.wins)

    print(f'simulation time: {simulation_time}')
    print(f'    time to select: {total_select_time}, time to playout: {total_playout_time}, time to pick best: {time() - curr_time}')
    print('playout breakdown:')
    print(f'    shuffle: {time_struct.shuffle}, find valid: {time_struct.find_valid}')
    print(f'toal time taken: {time() - turn_start_time}')

    # for some reason if there is only one valid move the ai will choose an invalid move
    if not board.is_place_valid(best_move.node.placement, color):
        best_move = root_tree_node.node.generate_nodes(pieces)[0]
        return best_move.placement

    return best_move.node.placement
