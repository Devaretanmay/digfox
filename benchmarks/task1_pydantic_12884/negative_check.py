#!/usr/bin/env python3
"""
Negative test case: verifies that raw Pydantic v2 fails to preserve the validated field under collision.
Exit code 1 on defect detection confirms the failure condition.
"""

import sys
from pydantic import BaseModel, ConfigDict, Field


class CollisionModel(BaseModel):
    model_config = ConfigDict(extra='allow')
    x: int = Field(alias='X')


payload = {'X': 1, 'x': 2}
model = CollisionModel.model_validate(payload)
dumped = model.model_dump()

if dumped.get('x') != 1:
    print(f"FAILURE REPRODUCED: model.x expected 1, but got {dumped.get('x')} due to collision with extra['x']")
    sys.exit(1)
else:
    print("SUCCESS: model.x preserved")
    sys.exit(0)
