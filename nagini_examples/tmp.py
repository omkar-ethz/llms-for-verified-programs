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

def reverseList(head: Node) -> Optional[Node]:
    """Reverses the list and returns the new head."""
    Requires(is_list(head))
    Ensures(Implies(Result() is not None, is_list(Result())))

    Unfold(is_list(head))
    if head.next is None:
        Fold(is_list(head))
        return head
    prev = None # type: Optional[Node]
    ptr = head # type: Optional[Node]
    while ptr != None:
        Invariant(Implies(ptr is not None, is_list(ptr)))
        Unfold(is_list(ptr))
        tmp = ptr.next
        Unfold(is_list(tmp))
        ptr.next = prev
        Fold(is_list(ptr))
        Fold(is_list(tmp))
        prev = ptr
        ptr = tmp
        Fold(is_list(prev))
    Fold(is_list(ptr))
    return prev