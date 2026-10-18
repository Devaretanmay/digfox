"""Fixture and acceptance test for Task 3: Ruff #28861."""

import re
import unittest


def unpatched_remove_useless_return(source_line: str) -> str:
    # Simulates the flawed fix: stripping the return and everything after it
    if re.match(r'^\s*return\b', source_line):
        return ''
    return source_line


def safe_remove_useless_return(source_line: str) -> str:
    # Preserves comments attached to the return statement
    match = re.match(r'^(\s*)return(?:\s+(#.*))?$', source_line)
    if match:
        indent = match.group(1)
        comment = match.group(2)
        if comment:
            return f"{indent}{comment}"
        return ''
    return source_line


class TestTask3Acceptance(unittest.TestCase):
    def test_reproduction_comment_loss(self):
        line = "    return # subSchema.__init__()"
        flawed = unpatched_remove_useless_return(line)
        self.assertEqual(flawed, '')

    def test_safe_removal_preserves_comment(self):
        line = "    return # subSchema.__init__()"
        safe = safe_remove_useless_return(line)
        self.assertEqual(safe, "    # subSchema.__init__()")

    def test_safe_removal_bare_return(self):
        line = "    return"
        safe = safe_remove_useless_return(line)
        self.assertEqual(safe, '')

    def test_regression_safety_non_useless_return(self):
        line = "    return x + 1 # returns sum"
        safe = safe_remove_useless_return(line)
        self.assertEqual(safe, line)


if __name__ == '__main__':
    unittest.main()
