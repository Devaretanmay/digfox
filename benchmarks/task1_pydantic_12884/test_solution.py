"""
Unit and regression tests for Task 1: Pydantic issue #12884.
Tests reproduction, validated field preservation, collision handling, and regression safety.
"""

import json
import unittest
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class CollisionModel(BaseModel):
    model_config = ConfigDict(extra='allow')
    x: int = Field(alias='X')


class StandardModel(BaseModel):
    model_config = ConfigDict(extra='allow')
    title: str
    count: int = 0


def safe_model_dump(model: BaseModel, by_alias: bool = False, **kwargs: Any) -> Dict[str, Any]:
    """
    Reference resolution for issue #12884:
    Preserves validated field values and prevents model_extra collisions from overwriting them.
    """
    raw_dump = model.model_dump(by_alias=by_alias, **kwargs)
    extra = model.model_extra or {}
    if not extra:
        return raw_dump

    # Determine declared field output names
    for field_name, field_info in model.__class__.model_fields.items():
        output_key = field_info.alias if (by_alias and field_info.alias) else field_name
        validated_val = getattr(model, field_name)

        # If model_extra had a collision that overwrote output_key with unvalidated extra data:
        if output_key in extra and raw_dump.get(output_key) != validated_val:
            raw_dump[output_key] = validated_val

    return raw_dump


def safe_model_dump_json(model: BaseModel, by_alias: bool = False, **kwargs: Any) -> str:
    """
    Safe JSON serialization ensuring valid single-occurrence keys.
    """
    dumped = safe_model_dump(model, by_alias=by_alias, **kwargs)
    return json.dumps(dumped)


class TestTask1Pydantic12884(unittest.TestCase):
    def test_reproduction_demonstrates_raw_collision(self):
        """Verify the raw Pydantic behavior exhibits the reported issue #12884 collision."""
        payload = {'X': 1, 'x': 2}
        model = CollisionModel.model_validate(payload)

        self.assertEqual(model.x, 1)
        self.assertEqual(model.model_extra, {'x': 2})

        raw_dump = model.model_dump()
        # In unpatched Pydantic v2, extra 'x' (2) overwrites validated 'x' (1)
        self.assertEqual(raw_dump.get('x'), 2)

    def test_safe_dump_preserves_validated_value(self):
        """Verify safe serialization preserves validated field value x=1."""
        payload = {'X': 1, 'x': 2}
        model = CollisionModel.model_validate(payload)

        resolved_dump = safe_model_dump(model, by_alias=False)
        self.assertEqual(resolved_dump.get('x'), 1)

    def test_safe_dump_by_alias(self):
        """When by_alias=True, alias X and extra x do not collide."""
        payload = {'X': 1, 'x': 2}
        model = CollisionModel.model_validate(payload)

        resolved_dump = safe_model_dump(model, by_alias=True)
        self.assertEqual(resolved_dump.get('X'), 1)
        self.assertEqual(resolved_dump.get('x'), 2)

    def test_safe_dump_json_produces_valid_unique_keys(self):
        """Verify JSON dump emits valid JSON with no duplicate key confusion."""
        payload = {'X': 1, 'x': 2}
        model = CollisionModel.model_validate(payload)

        json_str = safe_model_dump_json(model, by_alias=False)
        parsed = json.loads(json_str)
        self.assertEqual(parsed.get('x'), 1)

    def test_regression_standard_model_without_collision(self):
        """Ensure models without collisions serialize identically to standard Pydantic."""
        model = StandardModel(title="test", count=5, custom_tag="alpha")
        standard_dump = model.model_dump()
        resolved_dump = safe_model_dump(model)

        self.assertEqual(standard_dump, resolved_dump)
        self.assertEqual(resolved_dump['title'], "test")
        self.assertEqual(resolved_dump['count'], 5)
        self.assertEqual(resolved_dump['custom_tag'], "alpha")


if __name__ == '__main__':
    unittest.main()
