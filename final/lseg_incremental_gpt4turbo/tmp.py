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

from nagini_contracts.contracts import *
from nagini_contracts.io_builtins import *
from typing import Optional

class Node:
    def __init__(self, val: int, next: Optional['Node']) -> None:
        self.val = val
        self.next = next

@Predicate
def lseg(first: Optional[Node], last: Optional[Node]) -> bool:
    return Implies(
        first is not last, Acc(first.val) and Acc(first.next) and lseg(first.next, last)
    )

@Requires(Acc(lseg(first, last), 1/2))
@Ensures(Acc(lseg(Result(), last), 1/2))
@Ensures(Implies(first is not last, Result() is first.next))
def remove_first(first: Node, last: Node) -> Optional[Node]:
    """Remove the first node from the list."""
    if first is last:
        return last
    Unfold(lseg(first, last))
    rest = first.next
    Fold(lseg(rest, last))
    return rest