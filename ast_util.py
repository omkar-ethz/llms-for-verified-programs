"""AST analysis and manipulation of a source program for the purpose of dataset generation."""
import dataclasses
import itertools
import copy
import ast
import numpy as np
from typing import Iterator, Sequence, TypeVar

T = TypeVar("T")


def powerset(s: Sequence[T]) -> Iterator[Sequence[T]]:
    """Generates the power set of a given set."""
    g = (itertools.combinations(s, r) for r in range(len(s) + 1))
    return itertools.chain.from_iterable(g)


@dataclasses.dataclass
class Annotation:
    """Represents an annotation in a program."""

    name: str
    line: int
    col: int


class AnnotationAnalyzer(ast.NodeVisitor):
    """Analyzes the AST of a program to find the line numbers of annotations."""

    def __init__(self) -> None:
        super().__init__()
        self.annotations: list[Annotation] = []

    def visit_Expr(self, node: ast.Expr) -> None:
        """Visit Expr nodes"""
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id
            in [
                "Requires",
                "Ensures",
                "Unfold",
                "Fold",
                "Invariant",
            ]
        ):
            self.annotations.append(
                Annotation(node.value.func.id, node.lineno, node.col_offset)
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit Call nodes"""
        if isinstance(node.func, ast.Name) and node.func.id == "Unfolding":
            self.annotations.append(
                Annotation(node.func.id, node.lineno, node.col_offset)
            )
        self.generic_visit(node)


class AnnotationRemover(ast.NodeTransformer):
    """Removes annotations from the AST of a program."""

    def __init__(self, annotations: Sequence[Annotation]) -> None:
        super().__init__()
        self.annotations = annotations

    def visit_Expr(self, node: ast.Expr) -> ast.Expr | None:
        """Visit Expr nodes"""
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and Annotation(node.value.func.id, node.lineno, node.col_offset) in self.annotations
        ):
            return None
        return node

    def visit_Call(self, node: ast.Call) -> ast.expr | None:
        """Visit Call nodes"""
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "Unfolding"
            and Annotation(node.func.id, node.lineno, node.col_offset)  in self.annotations
        ):
            return node.args[1]
        return node


def dataset_generator(program: ast.AST) -> Iterator[ast.AST]:
    """Generates a dataset of programs with different combinations of annotations removed."""
    analyzer = AnnotationAnalyzer()
    analyzer.visit(program)
    annotations = analyzer.annotations
    if len(annotations) > 10:
        annotations = np.random.choice(annotations, 10, replace=False).tolist() # type: ignore
    for subset in powerset(annotations):
        program_copy = copy.deepcopy(program)  # reset the program
        yield AnnotationRemover(subset).visit(program_copy)


# analyzer = AnnotationAnalyzer()
# analyzer.visit(x)
# print(analyzer.annotations)
# dataset = dataset_generator(x)
