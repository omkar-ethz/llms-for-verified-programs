from nagini_contracts.contracts import *
from typing import Optional, List

class Node:
    def __init__(self, val: int, next: "Node" = None) -> None:
        self.val = val
        self.next = next
        Ensures(
            Acc(self.val) and self.val is val and Acc(self.next) and self.next is next
        )

@Predicate
def is_list(head: Node) -> bool:
    return (
        head is not None
        and Acc(head.val)
        and Acc(head.next)
        and Implies(head.next is not None, is_list(head.next))
    )


def append(head: Node, val: int) -> None:
    Requires(is_list(head))
    Ensures(is_list(head))
    if head.next is None:
        Unfold(is_list(head))
        n = Node(val)
        Fold(is_list(n))
        head.next = n
        Fold(is_list(head))
    else:
        Unfold(is_list(head))
        append(head.next, val)
        Fold(is_list(head))
