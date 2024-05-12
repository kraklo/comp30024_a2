from time import time

from referee.game.actions import PlaceAction
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N
from referee.game.coord import Coord

from .node import Node
from .board_utils import Board
from .tree import Tree

MCTS_ITERATIONS = 200


def search(board: Board, color: PlayerColor, tree: Tree, time_remaining) -> PlaceAction:
    if not time_remaining:
        time_remaining = 180

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

    # simulate playouts
    for i in range(MCTS_ITERATIONS):
        if time() - turn_start_time >= min(9, time_remaining / 6):
            print(f'out of time! iterations ran: {i}')
            break

        # select a node
        tree_node = root_tree_node.select_max_child()

        if not tree_node:
            break

        while tree_node.playouts != 0:
            new_tree_node = tree_node.select_max_child()
            if not new_tree_node:
                break

            tree_node = new_tree_node

        # playout
        tree_node.playout()

    print("picking best move")
    # pick the best move
    best_move = root_tree_node.select_best_move()
    print(best_move.wins)

    # for some reason if there is only one valid move the ai will choose an invalid move
    if not board.is_place_valid(best_move.node.placement, color):
        best_move = root_tree_node.node.generate_nodes()[0]
        return best_move.placement

    return best_move.node.placement
