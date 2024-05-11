import math

from typing import Optional

from .board_utils import Board
from .node import Node
from referee.game import PlayerColor

BALANCING_CONSTANT = 2


class Tree:
    def __init__(self):
        self.nodes = {}

    def contained_transposed_board(self, board: Board) -> str:
        for key in self.nodes.keys():
            if board.is_transposition(self.nodes[key].node.board):
                return self.nodes[key].node.board.board_string

        return ''

    def add_tree_node(self, node: Node, parent: Optional['TreeNode']) -> 'TreeNode':
        transposed_str = self.contained_transposed_board(node.board)

        if transposed_str:
            return self.nodes[transposed_str]

        new_node = TreeNode(node, parent, self, node.board.board_to_string())
        self.nodes[node.board.board_string] = new_node

        return new_node

    def get_node_from_board(self, board: Board) -> Optional['TreeNode']:
        transposed_str = self.contained_transposed_board(board)

        if transposed_str:
            return self.nodes[transposed_str]

        return None


class TreeNode:
    def __init__(self, node: Node, parent: Optional['TreeNode'], tree: Tree, board_string: str):
        self.node = node
        self.parent = parent
        self.tree = tree
        self.board_string = board_string
        self.children = {}
        self.playouts = 0
        self.wins = 0

    def ucb(self) -> float:
        if self.playouts == 0 or self.parent.wins == 0:
            return float('inf')

        return ((self.wins / self.playouts)
                + BALANCING_CONSTANT * math.sqrt(math.log(self.parent.wins) / self.playouts))

    def back_propagate(self, winning_color: PlayerColor) -> None:
        self.playouts += 1

        if winning_color == self.node.color:
            self.wins += 1

        if self.parent:
            self.parent.back_propagate(winning_color)

    def playout(self) -> None:
        winning_color = self.node.playout()
        self.back_propagate(winning_color)

    def select_max_child(self) -> 'TreeNode':
        if len(self.children.keys()) == 0:
            child_nodes = self.node.generate_nodes()

            for node in child_nodes:
                child_node = self.tree.add_tree_node(node, self)
                self.children[child_node.board_string] = child_node

        max_ucb = float('-inf')
        max_node = None

        for key in self.children.keys():
            ucb = self.children[key].ucb()

            if ucb > max_ucb:
                max_ucb = ucb
                max_node = self.children[key]

        return max_node

    def select_best_move(self) -> 'TreeNode':
        max_proportion = float('-inf')
        max_node = None

        for key in self.children.keys():
            node = self.children[key]
            if node.playouts > 0:
                proportion = node.wins / node.playouts
            else:
                proportion = 0

            if proportion > max_proportion:
                max_proportion = proportion
                max_node = node

        return max_node
