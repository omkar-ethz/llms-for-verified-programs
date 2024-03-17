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

def count(head: Optional[Node]) -> int:
    """Counts the number of nodes in the list."""
    Requires(lseg(head, None))
    Ensures(lseg(head, None))
    if head is None:
        return 0
    Unfold(lseg(head, None))
    result = 1 + count(head.next)
    Fold(lseg(head, None))
    return result

def split(head: Optional[Node], idx: int) -> Optional[Node]:
    """Splits the list at the given index. Result is the list starting at idx."""
    Requires(lseg(head, None))
    Ensures(lseg(head, None) and lseg(Result(), None))
    if head is None:
        Fold(lseg(None, None))
        return None
    if idx == 1:
        Unfold(lseg(head, None))
        rest = head.next
        head.next = None
        Fold(lseg(None, None))
        Fold(lseg(head, None))
        return rest
    Unfold(lseg(head, None))
    rest = split(head.next, idx - 1)
    Fold(lseg(head, None))
    return rest

def merge(head1: Optional[Node], head2: Optional[Node]) -> Optional[Node]:
    """Merge two sorted lists."""
    Requires(lseg(head1, None) and lseg(head2, None))
    Ensures(lseg(Result(), None))
    if head1 is None:
        return head2
    if head2 is None:
        return head1
    if Unfolding(lseg(head1, None), head1.val) < Unfolding(
        lseg(head2, None), head2.val
    ):
        Unfold(lseg(head1, None))
        head1.next = merge(head1.next, head2)
        Fold(lseg(head1, None))
        return head1
    Unfold(lseg(head2, None))
    head2.next = merge(head1, head2.next)
    Fold(lseg(head2, None))
    return head2

def merge_sort(head: Optional[Node]) -> Optional[Node]:
    """Sorts the list using merge sort."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    if head is None or head.next is None:
        return head
    Unfold(lseg(head, None))
    mid = count(head) // 2
    lst = Unfolding(lseg(head, None), head.next)
    Unfold(lseg(head, None))
    rest = split(head, mid)
    Fold(lseg(rest, None))
    head = merge_sort(head)
    Fold(lseg(head, None))
    rest = merge_sort(rest)
    return merge(head, rest)

