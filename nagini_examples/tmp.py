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
    if head1 is None:
        return head2
    if head2 is None:
        return head1
    return join_lists_helper(head1, head2)

def join_lists_helper(head1: Optional[Node], head2: Optional[Node]) -> Optional[Node]:
    """Helper function for join_lists."""
    Requires(head1 is not None and is_list(head1))
    Requires(is_list(head2))
    Ensures(is_list(Result()))
    Unfold(is_list(head1))
    head1.next = join_lists_helper(head1.next, head2)
    Fold(is_list(head1))
    return head1