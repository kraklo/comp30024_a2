import math

from typing import Optional, List

from .board_utils import Board
from .node import Node
from referee.game import PlayerColor
from .tetromino import TetrominoShape

BALANCING_CONSTANT = 1


class Tree:
    def __init__(self):
        self.nodes = {}

    def add_tree_node(self, node: Node, parent: Optional['TreeNode']) -> 'TreeNode':
        transposition = self.nodes.get(node.board.board_string, None)

        if transposition:
            self.nodes[node.board.board_string].node = node
            return self.nodes[node.board.board_string]

        new_node = TreeNode(node, parent, self, node.board.board_string)
        self.nodes[node.board.board_string] = new_node

        return new_node

    def get_node_from_board(self, board: Board) -> Optional['TreeNode']:
        return self.nodes.get(board.board_string, None)


class TreeNode:
    def __init__(self, node: Node, parent: Optional['TreeNode'], tree: Tree, board_string: str):
        self.node = node
        self.parent = parent
        self.tree = tree
        self.board_string = board_string
        self.children = {}
        self.playouts = 0
        self.amaf_visits = 0
        self.amaf_wins = 0
        self.wins = 0
        self.ucb_score = float('inf')

    def ucb(self) -> float:
        if self.playouts == 0:
            return float('inf')

        if not self.parent or self.parent.wins == 0:
            return self.wins / self.playouts

        return ((self.wins / self.playouts)
                + BALANCING_CONSTANT * math.sqrt(math.log(self.parent.wins) / self.playouts))

    def back_propagate(self, winning_color: PlayerColor) -> None:
        self.playouts += 1

        if winning_color == self.node.color:
            self.wins += 1

        self.ucb_score = self.ucb()

        if self.parent:
            self.parent.back_propagate(winning_color)

    def playout(self, pieces: List[TetrominoShape]) -> None:
        winning_color = self.node.playout(pieces)
        self.back_propagate(winning_color)

    def select_max_child(self, pieces: List[TetrominoShape]) -> 'TreeNode':
        if len(self.children.keys()) == 0:
            child_nodes = self.node.generate_nodes(pieces)

            for node in child_nodes:
                child_node = self.tree.add_tree_node(node, self)
                self.children[child_node.board_string] = child_node

        max_ucb = float('-inf')
        max_node = None

        for key in self.children.keys():
            this_node = self.children[key]
            ucb = this_node.ucb_score

            if ucb == float('inf'):
                return this_node

            if ucb > max_ucb:
                max_ucb = ucb
                max_node = this_node

        return max_node

    def select_best_move(self) -> 'TreeNode':
        max_playouts = float('-inf')
        max_node = None

        for key in self.children.keys():
            node = self.children[key]

            if node.playouts > max_playouts and self.node.board.is_place_valid(node.node.placement, self.node.color):
                max_playouts = node.playouts
                max_node = node

        return max_node
