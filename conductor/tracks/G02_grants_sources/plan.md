# Implementation plan

- [x] Record scope and acceptance requirements.
- [x] Inspect current inputs, dependencies and relevant platform objects. The reviewed delivery source map and official authority pages were inspected; endpoint payloads remain unverified.
- [x] Implement: Convert the researched source map into configuration with authority, format, access, sample and coverage status.
- [x] Implement fallback: Add a fail-closed reviewed-import route for sources without a permitted feed/API; require source/row identity, evidence URL, timezone-aware observation, reviewer notes and explicit `Reviewed` status.
- [~] Verify: Verify NHMRC, MRFF, ARC, QH, EMF, Advance Queensland and local foundation intake; use reviewed import where feeds are unavailable. Authority-page/configuration evidence is complete, including additional Queensland Health, Metro North, Metro South, Torres and Cape and Cancer Council sources; live endpoint/feed verification remains open.
- [x] Record local and live evidence separately before closure; the catalogue marks unverified intake explicitly and does not promote it to a working feed.
