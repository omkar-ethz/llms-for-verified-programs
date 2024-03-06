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

def lemma_extend(a: Optional[Node], b: Optional[Node]) -> Optional[Node]:
    """Extend a list segment by one element and return the new last"""
    Requires(lseg(a, b) and Acc(b.next) and Acc(b.val))
    Ensures(lseg(a, Result()) and Result() is Old(b.next))
    if a is b:
        last = b.next
        Fold(lseg(last, last))
        Fold(lseg(b, last))
        return last
    Unfold(lseg(a, b))
    last = lemma_extend(a.next, b)
    Fold(lseg(a, last))
    return last

def lemma_append(a: Optional[Node], b: Optional[Node]) -> None:
    """Append two list segments."""
    Requires(lseg(a, b) and lseg(b, None))
    Ensures(lseg(a, None))
    if a is b:
        return
    Unfold(lseg(a, b))
    lemma_append(a.next, b)
    Fold(lseg(a, None))

def append(head: Optional[Node], val: int) -> Node:
    """Append a new node with value val to the list."""
    n = Node(val)
    if head is None:
        return n
    ptr = head  # type: Node
    while ptr.next is not None:
        tmp = ptr
        ptr = ptr.next
        lemma_extend(head, tmp)
    ptr.next = n
    lemma_append(head, ptr)
    return head
