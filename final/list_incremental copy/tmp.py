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

def contains(head: Node, val: int) -> bool:
    """Returns True if the list contains the given value."""
    Requires(is_list(head))
    Ensures(Implies(Result(), is_list(head)))
    if Unfolding(is_list(head), head.val) == val:
        return True
    if Unfolding(is_list(head), head.next) is None:
        return False
    result = contains(head.next, val)
    return result

This is not a correct solution, as it does not preserve the is_list predicate. The is_list predicate must be preserved for methods that do not modify the list.