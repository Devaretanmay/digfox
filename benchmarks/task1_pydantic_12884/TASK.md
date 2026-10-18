# Task 1: Fix data serialization collision under extra='allow'

* **Repository**: `pydantic/pydantic`
* **Issue**: [#12884](https://github.com/pydantic/pydantic/issues/12884)
* **Target component**: `BaseModel.model_dump()` and `BaseModel.model_dump_json()` serialization
* **Difficulty**: Medium

---

## Problem description

When a Pydantic model is configured with `extra='allow'` and has a field defined with an alias, supplying both the alias key and the declared field name in input data creates a collision:

```python
from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
  model_config = ConfigDict(extra='allow')
  x: int = Field(alias='X')


payload = {'X': 1, 'x': 2}
model = Model.model_validate(payload)
```

1. Validation populates `model.x = 1` from the alias `'X'`.
2. The remaining unused key `'x'` is placed into `model.model_extra = {'x': 2}`.
3. During default serialization with `model.model_dump()`, Pydantic generates output using the field's declared name (`'x'`).
4. When `model_extra` is merged into the output dictionary, the unvalidated extra value (`2`) overwrites the validated field value (`1`), yielding `{'x': 2}`.
5. In `model.model_dump_json()`, duplicate keys are emitted: `{"x":1,"x":2}`.

---

## Expected behavior

1. Serializing a validated model must preserve validated field values. An extra field key that matches a declared field name must not silently overwrite the validated field value in `model_dump()`.
2. When alias output is requested via `by_alias=True`, both the alias key (`'X': 1`) and the extra key (`'x': 2`) may coexist if they do not collide on the serialized key name.
3. When serialized key names collide, the validated field value must take precedence over extra fields.
4. JSON serialization (`model_dump_json()`) must emit valid JSON with unique keys.

---

## Acceptance criteria

* **Correctness**: `model_dump()` preserves validated field data when collisions occur between declared field names and extra field keys.
* **Regression safety**: Models without extra fields or without key collisions must serialize with identical behavior to standard Pydantic models.
* **Integrity**: All tests must run and pass against Python 3.10+ and Pydantic V2.
