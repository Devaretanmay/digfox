# Fragment: cross-boundary diagnosis

Read only when observed behavior crosses a subsystem boundary.

- **API / service:** follow request validation, auth context, retries, exceptions, response mapping and alternate entry points.
- **Database:** inspect tenant scopes, transactions, isolation, query filters, migrations and rollback behavior.
- **Async / concurrency:** trace awaited work, scheduling, cancellation, idempotency, shared state and races.
- **Native / generated:** locate the implementation owner, bindings, serialization contracts and generated artifacts.
- Confirm which layer owns the bug and whether that layer is editable and testable. Do not hide an inaccessible owner behind recursive wrappers. Label a blocked repair as blocked.
- Test one path that bypasses the suspected fix before declaring it complete.
