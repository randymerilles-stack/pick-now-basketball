# Oddize credential staging and execution review
Reviewed 29 October 2026. No key was copied, read back, logged, committed or activated.

Current facts:
- Existing Render service remains Free, workspace tea-dbac8g8m7kps7389qajg, service srv-dbbd6mff3r2c738f4nsg. Existing login/runtime is unchanged.
- Current app.py has no Oddize consumer or research HTTP route. An environment variable alone cannot execute oddize_capture.py.
- Seven local HTTP/collector tests passed. With a synthetic key present, unauthorized research GET is 401; authenticated GET/HEAD and POST remain 404. Health is 200. No odds or existing feed callback executes.
- These are local checks against current GitHub source, not live release acceptance.

Configuration source of truth: existing service Dashboard/environment configuration. Do not introduce a competing Blueprint, environment group, secret file, duplicate service or paid job.

Safe staging, only when owner is ready:
1. Owner creates the free data-source account and API key. Never send password/key in chat, screenshots, source, command history or logs.
2. The existing service Environment page can hold PICKNOW_ODDIZE_API_KEY. For staging select **Save only**. Preserve all other variables, especially password/session/database settings.
3. This does not activate the value. Do not select either deploy option merely to store the key.
4. Do not retrieve/display the value through tools. Future code should read it inside the runtime and return only bounded, redacted sports evidence.

Execution prerequisite remains unfinished:
A tested, explicitly enabled private runtime consumer and authenticated operator path are needed for an autonomous Render-side sample. Caller authentication, request budget/idempotency, redirects, output redaction, persistence, full repository checks and actual release verification must be resolved before activation. No route is claimed to exist. Do not assume an owner cookie from a phone is available to automation.
An owner-run local process could instead execute the tested collector, but this is not autonomous hosting and should not be described as one.

Platform constraints verified directly from Render Markdown docs:
- Dashboard supports Save only, deployment of an existing build, or rebuild+deploy.
- Free services have no shell/SSH or one-off jobs, and local SQLite is ephemeral.
- No paid service/subscription is authorized. Existing Neon auth must remain untouched.

References read successfully via direct HTTP200 Markdown retrieval:
- https://render.com/docs/configure-environment-variables.md
- https://render.com/docs/free.md
Skill used: render-env-vars, including its environment-variables reference.
Docs describe platform behavior, not a credential transfer that has happened.

Next: implement/review the private consumer on an isolated branch with no real key and no deployment. Keep PAPER ONLY, source registry unapproved and Priority Pick unavailable. Free key availability does not establish live latency, quote-state alignment or a validated model.
