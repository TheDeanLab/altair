import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_FILES = tuple(sorted((REPO_ROOT / "simulations").glob("**/*.py")))


def _iter_functions(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            yield node


def _function_location(path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    return f"{path.relative_to(REPO_ROOT)}:{node.lineno} {node.name}"


def _parameter_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    args = [
        *node.args.posonlyargs,
        *node.args.args,
        *node.args.kwonlyargs,
    ]
    return [arg.arg for arg in args if arg.arg not in {"self", "cls"}]


def _annotation_missing(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    missing = [
        arg.arg
        for arg in (
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        )
        if arg.arg not in {"self", "cls"} and arg.annotation is None
    ]
    if node.args.vararg is not None and node.args.vararg.annotation is None:
        missing.append(node.args.vararg.arg)
    if node.args.kwarg is not None and node.args.kwarg.annotation is None:
        missing.append(node.args.kwarg.arg)
    if node.returns is None:
        missing.append("return")
    return missing


def _returns_none(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    annotation = node.returns
    if annotation is None:
        return False
    if isinstance(annotation, ast.Constant):
        return annotation.value is None
    return isinstance(annotation, ast.Name) and annotation.id == "None"


def _has_yield(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(isinstance(child, ast.Yield | ast.YieldFrom) for child in ast.walk(node))


def test_simulation_methods_have_type_hints():
    failures: list[str] = []
    for path in SIMULATION_FILES:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in _iter_functions(tree):
            missing = _annotation_missing(node)
            if missing:
                failures.append(f"{_function_location(path, node)} missing {missing}")

    assert not failures, "\n".join(failures)


def test_simulation_methods_use_numpydoc_sections():
    failures: list[str] = []
    for path in SIMULATION_FILES:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in _iter_functions(tree):
            docstring = ast.get_docstring(node) or ""
            location = _function_location(path, node)
            if not docstring:
                failures.append(f"{location} missing docstring")
                continue
            if _parameter_names(node) and "Parameters\n----------" not in docstring:
                failures.append(f"{location} missing numpydoc Parameters section")
            if not _returns_none(node):
                expected = "Yields\n------" if _has_yield(node) else "Returns\n-------"
                if expected not in docstring:
                    failures.append(
                        f"{location} missing numpydoc {expected.split()[0]}"
                    )

    assert not failures, "\n".join(failures)
