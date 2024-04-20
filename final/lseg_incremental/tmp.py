from typing import Optional
from nagini_contracts.contracts import *

class Node:
    def __init__(self, val: int, next: "Node" = None) -> None:
        self.val = val
        self.next = next
        Ensures(
            Acc(self.val) and self.val is val and Acc(self.next) and self.next is next
        )

@Predicate
def lseg(first: Optional[Node], last: Optional[Node]) -> bool:
    return Implies(
        first is not last, Acc(first.val) and Acc(first.next) and lseg(first.next, last)
    )

def reverse(head: Node) -> Optional[Node]:
    """Reverse the list segment."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    if Unfolding(lseg(head, None), head.next) is None:
        return head
    prev = None  # type: Optional[Node]
    ptr = head  # type: Optional[Node]
    while ptr is not None:
        Invariant(lseg(prev, None))
        Invariant(lseg(ptr, None))
        Unfold(lseg(ptr, None))
        tmp = ptr.next
        ptr.next = prev
        prev = ptr
        ptr = tmp
        if prev is not None:
            Fold(lseg(prev, prev))
        if ptr is not None:
            Fold(lseg(ptr, None))
    return prev