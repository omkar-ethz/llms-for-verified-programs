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

def join_lists(head1: Optional[Node], head2: Optional[Node]) -> Optional[Node]:
    """Returns the head of the list obtained by joining the two lists."""
    Requires(Implies(head1 is not None, is_list(head1)))
    Requires(Implies(head2 is not None, is_list(head2)))
    Ensures(Implies(Result() is not None, is_list(Result())))
    if head1 is None:
        return head2
    Unfold(is_list(head1))
    if head2 is None:
        Fold(is_list(head1))
        return head1
    head1.next = join_lists(head1.next, head2)
    Fold(is_list(head1))
    return head1