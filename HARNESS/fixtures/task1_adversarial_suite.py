"""
Adversarial Acceptance Test Suite for Pydantic Serialization Collision (Issue #12884).

This suite tests the library implementation directly against complex real-world serialization scenarios:
1. Deeply nested models with alias collisions at multiple depths.
2. Models inside collections (lists, tuples, dict values, dict keys).
3. Shared object identity / multi-reference models.
4. Self-referential / recursive model structures.
5. Models with custom field serializers (@field_serializer).
6. Models with computed fields (@computed_field).
7. Nested field inclusion and exclusion filtering (include/exclude mapping).
8. Validation alias vs serialization alias divergence.
9. JSON string format verification (no duplicate keys in raw JSON).
10. Serialization via TypeAdapter (direct engine delegation path).
11. Model state and input immutability verification.
12. High-volume extras scalability (stressing extra dict filtering).
"""

import json
import re
import unittest
from typing import Dict, List, Optional, Tuple, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    computed_field,
    field_serializer,
)


class TestPydanticAdversarialSerialization(unittest.TestCase):

    def test_01_deeply_nested_models(self):
        """Depth-4 model chain with alias collisions at alternating depths."""
        class Level4(BaseModel):
            model_config = ConfigDict(extra="allow")
            val: int = Field(alias="VAL")

        class Level3(BaseModel):
            model_config = ConfigDict(extra="allow")
            child: Level4

        class Level2(BaseModel):
            model_config = ConfigDict(extra="allow")
            child: Level3
            val2: str = Field(alias="VAL2")

        class Level1(BaseModel):
            model_config = ConfigDict(extra="allow")
            child: Level2

        m4 = Level4.model_validate({"VAL": 40, "val": 999})
        m3 = Level3.model_validate({"child": m4, "other_extra": "ok3"})
        m2 = Level2.model_validate({"child": m3, "VAL2": "correct2", "val2": "extra2"})
        m1 = Level1.model_validate({"child": m2, "root_extra": "ok1"})

        dumped = m1.model_dump()
        self.assertEqual(dumped["child"]["child"]["child"]["val"], 40)
        self.assertEqual(dumped["child"]["val2"], "correct2")

        dumped_json = json.loads(m1.model_dump_json())
        self.assertEqual(dumped_json["child"]["child"]["child"]["val"], 40)
        self.assertEqual(dumped_json["child"]["val2"], "correct2")

    def test_02_models_in_collections(self):
        """Models inside lists, tuples, and dictionary values."""
        class Item(BaseModel):
            model_config = ConfigDict(extra="allow")
            code: str = Field(alias="CODE")

        class Container(BaseModel):
            model_config = ConfigDict(extra="allow")
            items_list: List[Item]
            items_tuple: Tuple[Item, ...]
            items_dict: Dict[str, Item]

        i1 = Item.model_validate({"CODE": "A", "code": "ERR_A"})
        i2 = Item.model_validate({"CODE": "B", "code": "ERR_B"})
        i3 = Item.model_validate({"CODE": "C", "code": "ERR_C"})

        container = Container.model_validate({
            "items_list": [i1],
            "items_tuple": (i2,),
            "items_dict": {"key": i3}
        })

        dumped = container.model_dump()
        self.assertEqual(dumped["items_list"][0]["code"], "A")
        self.assertEqual(dumped["items_tuple"][0]["code"], "B")
        self.assertEqual(dumped["items_dict"]["key"]["code"], "C")

    def test_03_shared_object_identity(self):
        """Two fields referencing the identical child model instance."""
        class SharedChild(BaseModel):
            model_config = ConfigDict(extra="allow")
            val: int = Field(alias="VAL")

        class Parent(BaseModel):
            left: SharedChild
            right: SharedChild

        child = SharedChild.model_validate({"VAL": 100, "val": 999})
        parent = Parent(left=child, right=child)

        dumped = parent.model_dump()
        self.assertEqual(dumped["left"]["val"], 100)
        self.assertEqual(dumped["right"]["val"], 100)
        # Original child object should remain unmodified
        self.assertEqual(child.val, 100)
        self.assertEqual(child.model_extra, {"val": 999})

    def test_04_recursive_structures(self):
        """Self-referential linked list model."""
        class Node(BaseModel):
            model_config = ConfigDict(extra="allow")
            name: str = Field(alias="NAME")
            next_node: Optional["Node"] = None

        n2 = Node.model_validate({"NAME": "second", "name": "bad_second"})
        n1 = Node.model_validate({"NAME": "first", "name": "bad_first", "next_node": n2})

        dumped = n1.model_dump()
        self.assertEqual(dumped["name"], "first")
        self.assertIsNotNone(dumped["next_node"])
        self.assertEqual(dumped["next_node"]["name"], "second")

    def test_05_custom_field_serializers(self):
        """Custom field serializer modifying output."""
        class SerializerModel(BaseModel):
            model_config = ConfigDict(extra="allow")
            num: int = Field(alias="NUM")

            @field_serializer("num")
            def serialize_num(self, v: int, _info) -> str:
                return f"NUM-{v}"

        model = SerializerModel.model_validate({"NUM": 42, "num": 999})
        dumped = model.model_dump()
        self.assertEqual(dumped["num"], "NUM-42")

        dumped_json = json.loads(model.model_dump_json())
        self.assertEqual(dumped_json["num"], "NUM-42")

    def test_06_computed_fields(self):
        """Model with computed fields."""
        class ComputedModel(BaseModel):
            model_config = ConfigDict(extra="allow")
            base: int = Field(alias="BASE")

            @computed_field
            @property
            def doubled(self) -> int:
                return self.base * 2

        model = ComputedModel.model_validate({"BASE": 21, "base": 999})
        dumped = model.model_dump()
        self.assertEqual(dumped["base"], 21)
        self.assertEqual(dumped["doubled"], 42)

    def test_07_nested_include_exclude_filtering(self):
        """Granular include and exclude filtering on nested models."""
        class Child(BaseModel):
            model_config = ConfigDict(extra="allow")
            keep: int = Field(alias="KEEP")
            drop: int = Field(alias="DROP")

        class Root(BaseModel):
            child: Child

        c = Child.model_validate({"KEEP": 1, "keep": 100, "DROP": 2, "drop": 200})
        root = Root(child=c)

        dumped = root.model_dump(exclude={"child": {"drop"}})
        self.assertEqual(dumped["child"]["keep"], 1)
        self.assertNotIn("drop", dumped["child"])

    def test_08_validation_alias_vs_serialization_alias(self):
        """Divergent validation and serialization aliases."""
        class DualAliasModel(BaseModel):
            model_config = ConfigDict(extra="allow")
            attr: str = Field(validation_alias="in_attr", serialization_alias="out_attr")

        # Input provided via in_attr (validated) plus colliding extra attr
        model = DualAliasModel.model_validate({"in_attr": "VALID", "attr": "EXTRA", "out_attr": "OUT_EXTRA"})
        # When serialized by alias: key should be out_attr with VALID value
        dumped_alias = model.model_dump(by_alias=True)
        self.assertEqual(dumped_alias["out_attr"], "VALID")

        # When serialized without alias: key should be attr with VALID value
        dumped_name = model.model_dump(by_alias=False)
        self.assertEqual(dumped_name["attr"], "VALID")

    def test_09_model_dump_json_no_duplicate_keys(self):
        """Direct inspection of raw JSON output to verify no duplicate key emissions."""
        class RawJsonModel(BaseModel):
            model_config = ConfigDict(extra="allow")
            x: int = Field(alias="X")

        model = RawJsonModel.model_validate({"X": 10, "x": 20})
        raw_json = model.model_dump_json()

        # Regex check: "x" should appear exactly once as a key in the JSON string
        matches = re.findall(r'"x"\s*:', raw_json)
        self.assertEqual(len(matches), 1, f"Duplicate keys detected in JSON output: {raw_json}")

    def test_10_direct_typeadapter_serialization(self):
        """Direct serialization via TypeAdapter bypassing BaseModel.model_dump."""
        class Item(BaseModel):
            model_config = ConfigDict(extra="allow")
            x: int = Field(alias="X")

        item = Item.model_validate({"X": 5, "x": 99})
        adapter = TypeAdapter(Item)
        dumped = adapter.dump_python(item)
        self.assertEqual(dumped["x"], 5)

    def test_11_model_immutability(self):
        """Calling model_dump must not mutate original model state or identity."""
        class Child(BaseModel):
            model_config = ConfigDict(extra="allow")
            x: int = Field(alias="X")

        class Parent(BaseModel):
            child: Child

        c = Child.model_validate({"X": 1, "x": 2})
        p = Parent(child=c)

        child_id_before = id(p.child)
        extra_before = dict(p.child.model_extra) if p.child.model_extra else {}

        _ = p.model_dump()

        child_id_after = id(p.child)
        extra_after = dict(p.child.model_extra) if p.child.model_extra else {}

        self.assertEqual(child_id_before, child_id_after, "Parent child identity changed after model_dump")
        self.assertEqual(extra_before, extra_after, "Model extra was mutated after model_dump")

    def test_12_high_volume_extras_scalability(self):
        """Model with 500 extra keys serialized correctly without degradation."""
        class ScalabilityModel(BaseModel):
            model_config = ConfigDict(extra="allow")
            val: int = Field(alias="VAL")

        data = {"VAL": 123, "val": 999}
        for i in range(500):
            data[f"extra_{i}"] = i

        model = ScalabilityModel.model_validate(data)
        dumped = model.model_dump()
        self.assertEqual(dumped["val"], 123)
        self.assertEqual(len(dumped), 501)  # 1 declared field + 500 extras


if __name__ == "__main__":
    unittest.main()
