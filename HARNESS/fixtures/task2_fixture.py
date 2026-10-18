"""Fixture and acceptance test for Task 2: Pydantic #13734."""

import unittest
from unittest.mock import call
from typing import Any, Callable, Optional
from pydantic_core import to_jsonable_python


def safe_to_jsonable_python(obj: Any, fallback: Optional[Callable[[Any], Any]] = None, **kwargs: Any) -> Any:
    try:
        # Check if object has a fake or non-SchemaSerializer __pydantic_serializer__ attribute
        if hasattr(obj, '__pydantic_serializer__'):
            ser = getattr(obj, '__pydantic_serializer__')
            # If ser is a mock object (such as unittest.mock._Call), bypass standard serialization
            if type(ser).__module__.startswith('unittest.mock'):
                if fallback is not None:
                    return fallback(obj)
                raise TypeError(f"Cannot serialize mock object: {obj!r}")
        return to_jsonable_python(obj, fallback=fallback, **kwargs)
    except TypeError as e:
        if 'SchemaSerializer' in str(e) and fallback is not None:
            return fallback(obj)
        raise


class TestTask2Acceptance(unittest.TestCase):
    def test_reproduction_mock_call_crashes(self):
        c = call(1, 2, 3)
        with self.assertRaises(TypeError) as ctx:
            to_jsonable_python(c, fallback=lambda x: list(x.args))
        self.assertIn("SchemaSerializer", str(ctx.exception))

    def test_safe_serialization_delegates_to_fallback(self):
        c = call(10, 'alpha', key='val')
        res = safe_to_jsonable_python(c, fallback=lambda x: {'args': list(x.args), 'kwargs': x.kwargs})
        self.assertEqual(res, {'args': [10, 'alpha'], 'kwargs': {'key': 'val'}})

    def test_regression_safety_standard_types(self):
        data = {'a': 1, 'b': [2, 3], 'c': 'text'}
        self.assertEqual(safe_to_jsonable_python(data), to_jsonable_python(data))


if __name__ == '__main__':
    unittest.main()
