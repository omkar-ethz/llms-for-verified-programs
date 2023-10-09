from nagini_contracts.contracts import *
from typing import Optional


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
        Acc(head.val)
        and Acc(head.next)
        and Implies(head.next is not None, is_list(head.next))
    )
