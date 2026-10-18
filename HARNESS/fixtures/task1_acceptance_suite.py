"""Comprehensive 10-point independent acceptance test suite for Pydantic #12884.

Tests against the in-tree Pydantic library:
1. Field aliases without explicit serialization aliases.
2. Different validation and serialization aliases.
3. serialize_by_alias=True configuration.
4. model_dump() with and without aliases.
5. model_dump_json() serialization integrity.
6. Nested models with extra field collisions.
7. Custom field serializers (@field_serializer).
8. Include and exclude parameter settings.
9. Non-colliding extra fields retention.
10. Model instance immutability (no mutation of original model).
"""

import sys
import json
import unittest
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class TestTask1ComprehensiveAcceptance(unittest.TestCase):
    def test_01_field_alias_without_serialization_alias(self):
        """Check 1: Field alias without explicit serialization alias."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(alias='X')

        m = Model.model_validate({'X': 1, 'x': 2})
        dumped = m.model_dump()
        self.assertEqual(dumped.get('x'), 1, f"Expected validated field value 1, got {dumped.get('x')}")

    def test_02_different_validation_and_serialization_aliases(self):
        """Check 2: Different validation and serialization aliases."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(validation_alias='in_x', serialization_alias='out_x')

        m = Model.model_validate({'in_x': 1, 'out_x': 2})
        dumped = m.model_dump(by_alias=True)
        self.assertEqual(dumped.get('out_x'), 1, f"Expected serialized value 1 for out_x, got {dumped.get('out_x')}")

    def test_03_serialize_by_alias_config(self):
        """Check 3: serialize_by_alias=True in model_config."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow', serialize_by_alias=True)
            x: int = Field(alias='X')

        m = Model.model_validate({'X': 1, 'x': 2})
        dumped = m.model_dump()
        self.assertEqual(dumped.get('X'), 1)
        self.assertEqual(dumped.get('x'), 2)

    def test_04_dump_with_and_without_aliases(self):
        """Check 4: model_dump() with and without aliases."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(alias='X')

        m = Model.model_validate({'X': 1, 'x': 2})
        dumped_no_alias = m.model_dump(by_alias=False)
        self.assertEqual(dumped_no_alias.get('x'), 1)

        dumped_alias = m.model_dump(by_alias=True)
        self.assertEqual(dumped_alias.get('X'), 1)
        self.assertEqual(dumped_alias.get('x'), 2)

    def test_05_model_dump_json(self):
        """Check 5: model_dump_json() serialization integrity."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(alias='X')

        m = Model.model_validate({'X': 1, 'x': 2})
        json_str = m.model_dump_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed.get('x'), 1)

    def test_06_nested_models(self):
        """Check 6: Nested models with collision in inner model."""
        class Inner(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(alias='X')

        class Outer(BaseModel):
            inner: Inner

        outer = Outer(inner=Inner.model_validate({'X': 10, 'x': 20}))
        dumped = outer.model_dump()
        self.assertEqual(dumped['inner'].get('x'), 10)

    def test_07_custom_field_serializers(self):
        """Check 7: Custom field serializers with extra collisions."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(alias='X')

            @field_serializer('x')
            def double_x(self, v: int) -> int:
                return v * 10

        m = Model.model_validate({'X': 5, 'x': 99})
        dumped = m.model_dump()
        self.assertEqual(dumped.get('x'), 50)

    def test_08_include_and_exclude(self):
        """Check 8: Include and exclude settings."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(alias='X')
            y: int = 10

        m = Model.model_validate({'X': 1, 'x': 2, 'y': 10})
        dumped_inc = m.model_dump(include={'x'})
        self.assertEqual(dumped_inc, {'x': 1})

        dumped_exc = m.model_dump(exclude={'x'})
        self.assertNotIn('x', dumped_exc)

    def test_09_non_colliding_extra_fields(self):
        """Check 9: Non-colliding extra fields retention."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(alias='X')

        m = Model.model_validate({'X': 1, 'x': 2, 'unrelated': 'extra_val'})
        dumped = m.model_dump()
        self.assertEqual(dumped.get('x'), 1)
        self.assertEqual(dumped.get('unrelated'), 'extra_val')

    def test_10_no_mutation_of_original_model(self):
        """Check 10: Original model instance must remain unmutated."""
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            x: int = Field(alias='X')

        m = Model.model_validate({'X': 1, 'x': 2, 'extra_key': 42})
        orig_extra = dict(m.model_extra) if m.model_extra else {}
        _ = m.model_dump()
        self.assertEqual(m.model_extra, orig_extra, "model_dump() must not mutate original model_extra")
        self.assertEqual(m.x, 1)


if __name__ == '__main__':
    unittest.main()
