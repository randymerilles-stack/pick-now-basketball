# No-cost persistent-login feasibility — 22 October 2026, 00:34 Perth

Scope: durable owner login with exact 30-day expiry, logout revocation and credential-change revocation across service replacements. No production settings changed.

Verified sources:
- https://render.com/docs/free : free Postgres expires 30 days after creation; not an enduring remembered-login store. Do not provision it as a permanent fix.
- https://render.com/docs/key-value : free Key Value lacks disk persistence; replacement can lose session state. Not a fix for the reported defect.
- https://neon.com/docs/introduction/plans : a Free plan exists with no monthly cost; quotas and availability limits still apply.
- https://neon.com/docs/connect/connect-from-any-app : connection requires an actual project/database/role and TLS connection string.
- https://supabase.com/docs/guides/platform/free-project-pausing : low-activity Free projects may pause after seven days. No Supabase project was created.

Access check: available integration discovery found Neon and Supabase, neither installed/connected. GitHub and Render alone do not grant access to either provider. Suggested Neon as the single next integration, not multiple new accounts. No connection, project, credentials or Free-plan quota has yet been verified.

Action required: install/connect Neon using the offered integration, authenticate the intended owner account, then verify access and the Free plan before provisioning. Never paste database passwords or connection strings into public GitHub or this report. After connection, implement a Postgres session adapter; the existing SQLite backend cannot directly connect to Neon.

Revalidated current GitHub durable_sessions.py and test_durable_sessions.py in an isolated directory: three tests passed, including separate-process authentication and durable logout deletion. This remains local backend verification, not live Render or phone acceptance. The actual login fix is not deployed. The 22 October 18:00 target cannot be guaranteed while datastore access remains missing.

Priority Pick remains independently blocked by undocumented provider clock/ref alignment, uncorroborated event aliases/odds and absence of qualified score/time training/evaluation records. Additional provider-only captures and tiny utility tests must not be presented as model validation.

Persistent access dependency now requires owner action. Pause the recurring development task rather than generate repeated reports with no deployable integration; resume after access is confirmed and reread DEVELOPMENT_STATUS.md. Preserve current private app access and PAPER ONLY gates.
