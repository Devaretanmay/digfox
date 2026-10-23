# Repair decisions

Read this file when more than one repair layer or migration path appears viable.

## Smallest complete change

Evaluate options in this order:

1. Remove behavior that is not required.
2. Reuse the repository's existing implementation or convention.
3. Use a standard-library or native platform feature.
4. Use a dependency already installed for this purpose.
5. Add the minimum clear implementation.

The selected option must cover all affected callers, tests, fixtures, configuration, exports, error paths, and compatibility contracts. Fewer changed lines do not justify an incomplete repair.

## Owning-layer test

Prefer a layer when all are true:

- It creates the incorrect behavior rather than only exposing it.
- Relevant entry points pass through it.
- The repository and authorization scope permit changing it.
- A focused test can verify the repair there.

If the owner is unavailable, check supported configuration or extension mechanisms. A workaround must be labeled partial when another relevant path can still fail.

## Option comparison

Compare viable repairs by:

- behavioral coverage;
- regression and migration risk;
- compatibility and rollback;
- implementation and maintenance cost;
- performance and operational effects;
- verification strength.

Reject options that add speculative flexibility, duplicate policy across layers, weaken a trust boundary, or hide an error. Document a deferred alternative only when a concrete trigger would make it preferable.
