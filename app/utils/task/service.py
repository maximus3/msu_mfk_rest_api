import ast
import operator as op


# supported operators
_allowed_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

# supported math funcs
_allowed_funcs = {
    'max': max,
    'min': min,
}


def eval_expr(expr: str) -> float:
    """
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    >>> eval_expr('max(1, 2)')
    2
    """
    return _eval(ast.parse(expr, mode='eval').body)


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Num):  # <number>
        return node.value  # type: ignore
    if isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return _allowed_operators[type(node.op)](  # type: ignore
            _eval(node.left), _eval(node.right)
        )
    if isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return _allowed_operators[type(node.op)](  # type: ignore
            _eval(node.operand)
        )
    if isinstance(node, ast.Call):  # <func: id, ctx> <args> <keywords>
        return _allowed_funcs[node.func.id](  # type: ignore
            *[_eval(arg) for arg in node.args]
        )
    raise TypeError(node)
