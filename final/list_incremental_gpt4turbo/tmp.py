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

@ContractOnly
def count(head: Optional[Node]) -> int:
    Requires(Acc(head.val) and Acc(head.next) and is_list(head))
    
    if head is None:
        return 0
    cnt = 1 + count(head.next)
    return cnt
@ContractOnly
def split(head: Optional[Node], idx: int) -> Optional[Node]:
    Requires(Acc(head.val) and Acc(head.next) and is_list(head))
    Ensures(Implies(Result() is not None, is_list(Result())))
    
    if head is None:
        return None
    if idx == 1:
        rest = head.next
        head.next = None
        return rest
    rest = split(head.next, idx - 1)
    return rest
@ContractOnly
def merge(head1: Optional[Node], head2: Optional[Node]) -> Optional[Node]:
    Requires(Acc(head1.val) and Acc(head1.next) and is_list(head1))
    Requires(Acc(head2.val) and Acc(head2.next) and is_list(head2))
    Ensures(Implies(Result() is not None, is_list(Result())))
    
    if head1 is None:
        return head2
    if head2 is None:
        return head1
    if head1.val < Unfolding(is_list(head2), head2.val):
        head1.next = merge(head1.next, head2)
        return head1
    head2.next = merge(head1, head2.next)
    return head2
@ContractOnly
def merge_sort(head: Optional[Node]) -> Optional[Node]:
    Requires(Acc(head.val) and Acc(head.next) and is_list(head))
    Ensures(Implies(Result() is not None, is_list(Result())))
    
    if head is None:
        return None
    if head.next is None:
        return head
    mid = count(head) // 2
    rest = split(head, mid)
    head = merge_sort(head)
    rest = merge_sort(rest)
    head = merge(head, rest)
    return head