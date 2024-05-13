from time import time
from typing import List
import random

from referee.game.actions import PlaceAction
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N
from referee.game.coord import Coord

from .node import Node
from .board_utils import Board
from .tetromino import TetrominoShape
from .tree import Tree

MCTS_ITERATIONS = 1000


def search(board: Board, color: PlayerColor, tree: Tree, pieces: List[TetrominoShape], time_remaining) -> PlaceAction:
    if not time_remaining:
        time_remaining = 180

    turn_start_time = time()
    root = Node(None, board, color)
    root_tree_node = tree.get_node_from_board(board)

    if not root_tree_node:
        root_tree_node = tree.add_tree_node(root, None)

    if board.is_first_turn(color):
        random_piece = random.choice(pieces)
        random_coord = random.choice(board.blank_coords())
        moved_piece = random_piece.move_to_coord(random_coord).coords
        placement = PlaceAction(moved_piece[0], moved_piece[1], moved_piece[2], moved_piece[3])
        
        return placement

    # simulate playouts
    for i in range(MCTS_ITERATIONS):
        if time() - turn_start_time >= min(9.0, time_remaining / 6):
            break

        # select a node
        tree_node = root_tree_node.select_max_child(pieces)

        if not tree_node:
            break

        while tree_node.playouts != 0:
            new_tree_node = tree_node.select_max_child(pieces)
            if not new_tree_node:
                break

            tree_node = new_tree_node

        # playout
        tree_node.playout(pieces)

    # pick the best move
    best_move = root_tree_node.select_best_move()

    # for some reason if there is only one valid move the ai will choose an invalid move
    if not board.is_place_valid(best_move.node.placement, color):
        print('how did we get here?')
        best_move = root_tree_node.node.generate_nodes(pieces)[0]
        return best_move.placement

    return best_move.node.placement
