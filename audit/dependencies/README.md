# Python3.15 dependency qualification

The23October2026 candidate targets Python3.15.1 and uv0.13.5. Exact hash locks
include direct and transitive dependencies, allowing development candidates.
See `python315-20261023.json` for actual local checks and version inventory.

Current canonical source has no Node package manifest or package-manager lock.
Node26.12.1 matches the latest official distribution observed. npm12.2.1 was
qualified using an isolated private cache; shared global npm11.20.0 remains
untouched because this repository has no npm build/runtime to promote.

Only clean canonical source is qualified here. In-flight native flows, raw
archives, checkpoints, authentication, unrelated dirty work, schedules and email
controls remain unchanged. Hosted exact-head checks and main verification are
separate promotion evidence; do not infer them from this local receipt.
