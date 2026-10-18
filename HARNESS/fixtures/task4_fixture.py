"""Fixture and acceptance test for Task 4: Ruff #29365."""

import unittest


def unpatched_generate_comprehension(var: str, iterable_expr: str, condition_expr: str) -> str:
    # Unparenthesized ternary leads to invalid Python syntax
    return f"[{var} for {var} in {iterable_expr} if {condition_expr}]"


def safe_generate_comprehension(var: str, iterable_expr: str, condition_expr: str) -> str:
    # Ternary / conditional expressions must be wrapped in parentheses
    clean_iter = iterable_expr.strip()
    if ' if ' in clean_iter and ' else ' in clean_iter:
        if not (clean_iter.startswith('(') and clean_iter.endswith(')')):
            clean_iter = f"({clean_iter})"
    return f"[{var} for {var} in {clean_iter} if {condition_expr}]"


class TestTask4Acceptance(unittest.TestCase):
    def test_reproduction_syntax_error(self):
        code = unpatched_generate_comprehension(
            "value",
            "[values] if isinstance(values, str) else values",
            "value not in allowed"
        )
        with self.assertRaises(SyntaxError):
            compile(code, "<test>", "eval")

    def test_safe_generation_compiles(self):
        code = safe_generate_comprehension(
            "value",
            "[values] if isinstance(values, str) else values",
            "value not in allowed"
        )
        compiled = compile(code, "<test>", "eval")
        self.assertIsNotNone(compiled)

    def test_safe_generation_executes_correctly(self):
        code = safe_generate_comprehension(
            "value",
            "[values] if isinstance(values, str) else values",
            "value not in allowed"
        )
        scope = {'values': 'hello', 'allowed': {'h', 'e'}}
        result = eval(code, scope)
        self.assertEqual(result, ['hello'])

        scope2 = {'values': ['a', 'b', 'c'], 'allowed': {'b'}}
        result2 = eval(code, scope2)
        self.assertEqual(result2, ['a', 'c'])

    def test_regression_safety_standard_iterable(self):
        code = safe_generate_comprehension("x", "items", "x > 0")
        self.assertEqual(code, "[x for x in items if x > 0]")


if __name__ == '__main__':
    unittest.main()
