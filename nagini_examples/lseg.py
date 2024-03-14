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


def append(head: Optional[Node], val: int) -> Node:
    """Append a new node with value val to the list."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    if head is None:
        n = Node(val)
        Fold(lseg(None, None))
        Fold(lseg(n, None))
        return n
    Unfold(lseg(head, None))
    head.next = append(head.next, val)
    Fold(lseg(head, None))
    return head


def join(a: Optional[Node], b: Optional[Node], c: Optional[Node]) -> None:
    """Join two list segments."""
    Requires(lseg(a, b) and lseg(b, c))
    Ensures(lseg(a, c))
    if b is c:
        return
    if a is b:
        return
    Unfold(lseg(a, b))
    join(a.next, b, c)
    Fold(lseg(a, c))


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
        Fold(lseg(ptr, ptr))
        Fold(lseg(tmp, ptr))
        join(first, tmp, ptr)  # Ensures lseg(first, ptr)
    join(first, ptr, last)
    return result


def append_iter(head: Optional[Node], val: int) -> Node:
    """Append a new node with value val to the list."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
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
        Fold(lseg(ptr, ptr))
        Fold(lseg(tmp, ptr))
        join(head, tmp, ptr)
    Unfold(lseg(ptr, None))
    ptr.next = n
    Fold(lseg(ptr, None))
    join(head, ptr, None)
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
        Fold(lseg(ptr, ptr))
        Fold(lseg(tmp, ptr))
        join(head, tmp, ptr)
        pos -= 1
    if ptr is None:
        return head
    Unfold(lseg(ptr, None))
    n = Node(val, ptr.next)
    Fold(lseg(n, None))
    ptr.next = n
    Fold(lseg(ptr, None))
    join(head, ptr, None)
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
            join(first, ptr, last)
            return index
        Unfold(lseg(ptr, last))
        tmp = ptr
        ptr = ptr.next
        Fold(lseg(ptr, ptr))
        Fold(lseg(tmp, ptr))
        join(first, tmp, ptr)
        index += 1
    join(first, ptr, last)
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


def insert_sorted(head: Optional[Node], node: Node) -> Node:
    """Insert a new node, given as an lseg with one element, in the sorted list and returns the new head"""
    Requires(lseg(head, None) and lseg(node, None))
    Ensures(lseg(Result(), None))
    if head is None:
        return node
    if Unfolding(lseg(node, None), node.val) < Unfolding(lseg(head, None), head.val):
        Unfold(lseg(node, None))
        node.next = head
        Fold(lseg(node, None))
        return node
    Unfold(lseg(head, None))
    head.next = insert_sorted(head.next, node)
    Fold(lseg(head, None))
    return head


def insertion_sort(head: Node) -> Node:
    """Sort the list using insertion sort and return the new head"""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    if head is None or Unfolding(lseg(head, None), head.next) is None:
        return head
    Unfold(lseg(head, None))
    sorted_rest = insertion_sort(head.next)
    head.next = None
    Fold(lseg(None, None))
    Fold(lseg(head, None))
    return insert_sorted(sorted_rest, head)


def insertion_sort_iter(head: Node) -> Node:
    """Sort the list using insertion sort."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    sorted_prefix = head  # type: Node
    Unfold(lseg(sorted_prefix, None))
    ptr = sorted_prefix.next  # type: Optional[Node]
    sorted_prefix.next = None
    Fold(lseg(None, None))
    Fold(lseg(sorted_prefix, None))
    while ptr is not None:
        Invariant(lseg(sorted_prefix, None))
        Invariant(lseg(ptr, None))
        Unfold(lseg(ptr, None))
        tmp = ptr
        ptr = ptr.next
        tmp.next = None
        Fold(lseg(None, None))
        Fold(lseg(tmp, None))
        sorted_prefix = insert_sorted_iter(sorted_prefix, tmp)
    return sorted_prefix


def insert_sorted_iter(head: Node, node: Node) -> Node:
    """Insert a new node, given as an lseg with one element, in the sorted list and returns the new head"""
    Requires(lseg(head, None) and lseg(node, None))
    Ensures(lseg(Result(), None))
    Unfold(lseg(node, None))
    val = node.val
    Fold(lseg(node, None))
    if val < Unfolding(lseg(head, None), head.val):
        Unfold(lseg(node, None))
        node.next = head
        Fold(lseg(node, None))
        return node
    ptr = head  # type: Node
    Fold(lseg(head, ptr))
    while Unfolding(
        lseg(ptr, None),
        ptr.next is not None and val >= Unfolding(lseg(ptr.next, None), ptr.next.val),
    ):
        Invariant(lseg(head, ptr))
        Invariant(lseg(ptr, None))
        Unfold(lseg(ptr, None))
        tmp = ptr
        ptr = ptr.next
        Fold(lseg(ptr, ptr))
        Fold(lseg(tmp, ptr))
        join(head, tmp, ptr)
    Unfold(lseg(node, None))
    Unfold(lseg(ptr, None))
    node.next = ptr.next
    Fold(lseg(node, None))
    ptr.next = node
    Fold(lseg(ptr, None))
    join(head, ptr, None)
    return head


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


def count_iter(head: Optional[Node]) -> int:
    """Counts the number of nodes in the list."""
    Requires(lseg(head, None))
    Ensures(lseg(head, None))
    cnt = 0
    ptr = head  # type: Optional[Node]
    Fold(lseg(head, ptr))
    while ptr is not None:
        Invariant(lseg(head, ptr))
        Invariant(lseg(ptr, None))
        cnt += 1
        Unfold(lseg(ptr, None))
        tmp = ptr
        ptr = ptr.next
        Fold(lseg(ptr, ptr))
        Fold(lseg(tmp, ptr))
        join(head, tmp, ptr)
    join(head, ptr, None)
    return cnt


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


def split_iter(head: Optional[Node], idx: int) -> Optional[Node]:
    """Splits the list at the given index. Result is the list starting at idx."""
    Requires(lseg(head, None))
    Ensures(lseg(head, None) and lseg(Result(), None))
    if head is None:
        Fold(lseg(None, None))
        return None
    ptr = head  # type: Optional[Node]
    Fold(lseg(head, ptr))
    while idx > 1 and ptr is not None:
        Invariant(lseg(head, ptr))
        Invariant(lseg(ptr, None))
        Unfold(lseg(ptr, None))
        tmp = ptr
        ptr = ptr.next
        Fold(lseg(ptr, ptr))
        Fold(lseg(tmp, ptr))
        join(head, tmp, ptr)
        idx -= 1
    if ptr is None:
        return None
    Unfold(lseg(ptr, None))
    rest = ptr.next
    ptr.next = None
    Fold(lseg(None, None))
    Fold(lseg(ptr, None))
    join(head, ptr, None)
    return rest


def merge_sort(head: Optional[Node]) -> Optional[Node]:
    """Sorts the list using merge sort."""
    Requires(lseg(head, None))
    Ensures(lseg(Result(), None))
    if head is None or Unfolding(lseg(head, None), head.next) is None:
        return head
    mid = count(head) // 2
    rest = split(head, mid)
    head = merge_sort(head)
    rest = merge_sort(rest)
    return merge(head, rest)


def merge_iter(head1: Optional[Node], head2: Optional[Node]) -> Optional[Node]:
    """Merge two sorted lists."""
    Requires(lseg(head1, None) and lseg(head2, None))
    Ensures(lseg(Result(), None))
    if head1 is None:
        return head2
    if head2 is None:
        return head1
    result = Node(0)  # type: Node
    ptr = result # type: Node
    Fold(lseg(result, ptr))
    Fold(lseg(None, None))
    Fold(lseg(ptr, None))
    while head1 is not None and head2 is not None:
        Invariant(lseg(result, ptr))
        Invariant(lseg(ptr, None))
        Invariant(lseg(head1, None))
        Invariant(lseg(head2, None))
        Unfold(lseg(ptr, None))
        tmp = ptr
        if Unfolding(lseg(head1, None), head1.val) < Unfolding(lseg(head2, None), head2.val):
            Unfold(lseg(head1, None))
            ptr.next = head1
            head1 = head1.next
        else:
            Unfold(lseg(head2, None))
            ptr.next = head2
            head2 = head2.next
        ptr = ptr.next
        ptr.next = None
        Fold(lseg(None, None))
        Fold(lseg(ptr, None))
        Fold(lseg(ptr, ptr))
        Fold(lseg(tmp, ptr))
        join(result, tmp, ptr)
    Unfold(lseg(ptr, None))
    if head1 is not None:
        ptr.next = head1
    if head2 is not None:
        ptr.next = head2
    Fold(lseg(ptr, None))
    join(result, ptr, None)
    Unfold(lseg(result, None))
    return result.next
