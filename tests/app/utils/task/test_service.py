import pytest

from app.utils import task as task_utils


class TestEvalExpr:
    @pytest.mark.parametrize(
        'expr,value',
        [
            pytest.param('2**6', 64),
            pytest.param('1 + 2*3**(7-5) / (6 + -7)', -17),
            pytest.param('max(1, 2)', 2),
            pytest.param('min(1 + 2*3**(7-5) / (6 + -7), 2-6)', -17),
        ],
    )
    def test_ok(self, expr, value):
        assert task_utils.eval_expr(expr) == value
