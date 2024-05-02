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

def min_depth(root: Optional[TreeNode]) -> int:
    """Returns the number of nodes along the shortest path from the root node down to the nearest leaf node."""
    Requires(Implies(root is not None, tree(root)))
    Ensures(Implies(root is not None, tree(root)))
    if root is None:
        return 0
    Unfold(tree(root))
    if root.left is None and root.right is None:
        Fold(tree(root))
        return 1
    if root.left is None:
        d = 1 + min_depth(root.right)
        Fold(tree(root))
        return d
    if root.right is None:
        d = 1 + min_depth(root.left)
        Fold(tree(root))
        return d
    d = 1 + min(min_depth(root.left), min_depth(root.right))
    Fold(tree(root))
    return d