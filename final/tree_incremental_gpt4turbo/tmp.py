from typing import Optional
from nagini_contracts.contracts import *


class TreeNode:
    def __init__(
        self,
        key: int,
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
    ) -> None:
        self.key = key
        self.left = left
        self.right = right
        Ensures(
            Acc(self.key)
            and self.key is key
            and Acc(self.left)
            and self.left is left
            and Acc(self.right)
            and self.right is right
        )


@Predicate
def tree(n: TreeNode) -> bool:
    return (
        Acc(n.key)
        and Acc(n.left)
        and Acc(n.right)
        and Implies(n.left is not None, tree(n.left))
        and Implies(n.right is not None, tree(n.right))
    )

def sum_nodes(node: Optional[TreeNode]) -> int:
    """Returns the sum of the keys in the tree rooted at node"""
    Requires(tree(node))
    Ensures(tree(node))
    if node is None:
        return 0
    Unfold(tree(node))
    left_sum = 0 if node.left is None else sum_nodes(node.left)
    right_sum = 0 if node.right is None else sum_nodes(node.right)
    s = node.key + left_sum + right_sum
    Fold(tree(node))
    return s