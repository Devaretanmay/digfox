"""Fixture and acceptance test for Task 1: Pydantic #12884."""

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


def patch_model_dump(model: BaseModel, by_alias: bool = False, **kwargs: Any) -> Dict[str, Any]:
    raw_dump = model.model_dump(by_alias=by_alias, **kwargs)
    extra = model.model_extra or {}
    if not extra:
        return raw_dump
    for field_name, field_info in model.__class__.model_fields.items():
        output_key = field_info.alias if (by_alias and field_info.alias) else field_name
        validated_val = getattr(model, field_name)
        if output_key in extra and raw_dump.get(output_key) != validated_val:
            raw_dump[output_key] = validated_val
    return raw_dump


class TestTask1Acceptance(unittest.TestCase):
    def test_reproduction_collision_detected(self):
        payload = {'X': 1, 'x': 2}
        model = CollisionModel.model_validate(payload)
        raw_dump = model.model_dump()
        self.assertEqual(model.x, 1)
        self.assertEqual(model.model_extra, {'x': 2})
        self.assertEqual(raw_dump.get('x'), 2)

    def test_patched_dump_preserves_validated_field(self):
        payload = {'X': 1, 'x': 2}
        model = CollisionModel.model_validate(payload)
        safe_dump = patch_model_dump(model, by_alias=False)
        self.assertEqual(safe_dump.get('x'), 1)

    def test_patched_dump_by_alias(self):
        payload = {'X': 1, 'x': 2}
        model = CollisionModel.model_validate(payload)
        safe_dump = patch_model_dump(model, by_alias=True)
        self.assertEqual(safe_dump.get('X'), 1)
        self.assertEqual(safe_dump.get('x'), 2)

    def test_regression_safety_unaffected_models(self):
        model = StandardModel(title='test', count=5, custom_tag='alpha')
        self.assertEqual(model.model_dump(), patch_model_dump(model))


if __name__ == '__main__':
    unittest.main()
