"""Programs with verified memory safety specification for the list segment predicate."""

from typing import Optional, Tuple
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


def prepend(head: Optional[Node], val: int) -> Node:
    """Prepend a new node with value val to the list."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    n = Node(val, head)
    Fold(lseg(n, None))
    return n


def lemma_append(a: Optional[Node], b: Optional[Node]) -> None:
    """Append two list segments."""
    Requires(lseg(a, b) and lseg(b, None))
    Ensures(lseg(a, None))
    if a is b:
        return
    Unfold(lseg(a, b))
    lemma_append(a.next, b)
    Fold(lseg(a, None))


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


def lemma_assoc(a: Optional[Node], b: Optional[Node], c: Optional[Node]) -> None:
    """Associativity of list segment."""
    Requires(lseg(a, b) and lseg(b, c))
    Ensures(lseg(a, c))
    if b is c:
        return
    Unfold(lseg(b, c))
    b_new = lemma_extend(a, b)
    lemma_assoc(a, b_new, c)


def contains(first: Optional[Node], last: Optional[Node], val: int) -> bool:
    """Check if the list contains a node with value val."""
    Requires(lseg(first, last))
    Ensures(lseg(first, last))
    if first is None:
        return False
    if first is last:
        return False
    if Unfolding(lseg(first, last), first.val) == val:
        return True
    Unfold(lseg(first, last))
    result = contains(first.next, last, val)
    Fold(lseg(first, last))
    return result


def contains_iter(first: Node, last: Optional[Node], val: int) -> bool:
    """Check if the list contains a node with value val."""
    Requires(lseg(first, last))
    Ensures(lseg(first, last))
    ptr = first  # type: Optional[Node]
    result = False
    Fold(lseg(first, ptr))
    while ptr is not None and ptr is not last:
        Invariant(lseg(first, ptr))
        Invariant(lseg(ptr, last))
        if Unfolding(lseg(ptr, last), ptr.val) == val:
            result = True
            break
        Unfold(lseg(ptr, last))  # Ensures lseg(ptr.next, last)
        tmp = ptr
        ptr = ptr.next
        lemma_extend(first, tmp)  # Ensures lseg(first, ptr)
    lemma_assoc(first, ptr, last)
    return result


def append(head: Optional[Node], val: int) -> Node:
    """Append a new node with value val to the list."""
    Requires(lseg(head, None))
    Ensures(lseg(head, None))
    n = Node(val)
    Fold(lseg(None, None))
    Fold(lseg(n, None))
    if head is None:
        return n
    ptr = head  # type: Node
    Fold(lseg(head, ptr))
    while Unfolding(lseg(ptr, None), ptr.next) is not None:
        Invariant(lseg(head, ptr))
        Invariant(lseg(ptr, None))
        Unfold(lseg(ptr, None))
        tmp = ptr
        ptr = ptr.next
        lemma_extend(head, tmp)
    Unfold(lseg(ptr, None))
    ptr.next = n
    Fold(lseg(ptr, None))
    lemma_append(head, ptr)
    return head


def remove_first(first: Node, last: Node) -> Optional[Node]:
    """Remove the first node from the list."""
    Requires(lseg(first, last))
    Ensures(lseg(Result(), last))
    if first is last:
        return last
    Unfold(lseg(first, last))
    rest = first.next
    return rest


def remove_last(first: Optional[Node], last: Node) -> Optional[Node]:
    """Remove the last node from the list and returns the new last"""
    Requires(lseg(first, last))
    Ensures(lseg(first, Result()))
    if first is None:
        return last
    if first is last:
        return last
    Unfold(lseg(first, last))
    if first.next is last:
        Fold(lseg(first, first))
        return first
    rest = remove_last(first.next, last)
    Fold(lseg(first, rest))
    return rest


def insert(head: Optional[Node], val: int, pos: int) -> Optional[Node]:
    """Insert a new node with value val at position pos in the list."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    if pos == 0:
        return prepend(head, val)
    if head is None:
        return None
    Unfold(lseg(head, None))
    head.next = insert(head.next, val, pos - 1)
    Fold(lseg(head, None))
    return head


def insert_iter(head: Optional[Node], val: int, pos: int) -> Optional[Node]:
    """Insert a new node with value val at position pos in the list."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    if pos == 0:
        return prepend(head, val)
    if head is None:
        return None
    ptr = head  # type: Optional[Node]
    Fold(lseg(head, ptr))
    while pos > 1 and ptr is not None:
        Invariant(lseg(head, ptr))
        Invariant(lseg(ptr, None))
        Unfold(lseg(ptr, None))
        tmp = ptr
        ptr = ptr.next
        lemma_extend(head, tmp)
        pos -= 1
    if ptr is None:
        return head
    Unfold(lseg(ptr, None))
    n = Node(val, ptr.next)
    Fold(lseg(n, None))
    ptr.next = n
    lemma_extend(head, ptr)
    lemma_append(head, n)
    return head


def index_of(first: Node, last: Optional[Node], val: int) -> int:
    """Return the index of the first occurrence of val in the list or -1 if not found"""
    Requires(lseg(first, last))
    Ensures(lseg(first, last))
    ptr = first  # type: Optional[Node]
    Fold(lseg(first, ptr))
    index = 0
    while ptr is not None and ptr is not last:
        Invariant(lseg(first, ptr))
        Invariant(lseg(ptr, last))
        if Unfolding(lseg(ptr, last), ptr.val) == val:
            lemma_assoc(first, ptr, last)
            return index
        Unfold(lseg(ptr, last))
        tmp = ptr
        ptr = ptr.next
        lemma_extend(first, tmp)
        index += 1
    lemma_assoc(first, ptr, last)
    return -1


def reverse(head: Node) -> Optional[Node]:
    """Reverse the list segment."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    if Unfolding(lseg(head, None), head.next) is None:
        return head
    prev = None  # type: Optional[Node]
    ptr = head  # type: Optional[Node]
    Fold(lseg(prev, None))
    while ptr is not None:
        Invariant(lseg(prev, None))
        Invariant(lseg(ptr, None))
        Unfold(lseg(ptr, None))
        tmp = ptr.next
        ptr.next = prev
        prev = ptr
        ptr = tmp
        Fold(lseg(prev, None))
    return prev
