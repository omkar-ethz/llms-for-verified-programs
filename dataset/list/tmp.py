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

def merge_sort(head: Optional[Node]) -> Optional[Node]:
    """Sorts the list using merge sort."""
    Requires(Implies(head is not None, is_list(head)))
    Ensures(Implies(Result() is not None, is_list(Result())))
    if head is None:
        return None
    if Unfolding(is_list(head), head.next) is None:
        return head
    mid = max(1, count(head) // 2)
    rest = split(head, mid)
    head = merge_sort(head)
    rest = merge_sort(rest)
    head = merge(head, rest)
    return head

def split(head: Optional[Node], idx: int) -> Optional[Node]:
    """Splits the list at the given index. Result is the list starting at idx. Head to idx is also a list."""
    Requires(Implies(head is not None, is_list(head)) and idx > 0)
    Ensures(Implies(Result() is not None, is_list(Result())))
    if head is None:
        return None
    if idx == 1:
        Unfold(is_list(head))
        rest = head.next
        head.next = None
        Fold(is_list(head))
        return rest
    Unfold(is_list(head))
    rest = split(head.next, idx - 1)
    Fold(is_list(head))
    return rest
