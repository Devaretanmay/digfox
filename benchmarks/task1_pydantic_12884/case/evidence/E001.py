#!/usr/bin/env python3
"""
Task 1 Reproduction Script: Pydantic Issue #12884
Demonstrates serialization collision when extra='allow' and field aliases interact.
"""

import sys
from pydantic import BaseModel, ConfigDict, Field


class CollisionModel(BaseModel):
    model_config = ConfigDict(extra='allow')
    x: int = Field(alias='X')


def main() -> int:
    payload = {'X': 1, 'x': 2}
    model = CollisionModel.model_validate(payload)

    print("Target: pydantic issue #12884")
    print(f"Validated field value: model.x = {model.x}")
    print(f"Model extra fields: {model.model_extra}")

    dumped_default = model.model_dump()
    dumped_by_alias = model.model_dump(by_alias=True)
    dumped_json = model.model_dump_json()

    print(f"model_dump() output: {dumped_default}")
    print(f"model_dump(by_alias=True) output: {dumped_by_alias}")
    print(f"model_dump_json() output: {dumped_json}")

    # Detect the collision bug:
    # Under standard buggy behavior in pydantic v2, dumped_default['x'] is 2 (overwritten by extra)
    # instead of the validated value 1.
    if dumped_default.get('x') == 2:
        print("\nOBSERVED DEFECT: Validated field 'x' (value 1) was overwritten by extra field 'x' (value 2).")
        print("Bug reproduction: SUCCESSFUL")
        return 0
    elif dumped_default.get('x') == 1:
        print("\nOBSERVED FIX: Validated field 'x' retained its validated value 1.")
        return 0
    else:
        print(f"\nUNEXPECTED: model_dump returned {dumped_default}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
