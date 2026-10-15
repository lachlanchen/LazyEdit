# Studio agent runtime and portable deployment

## Routing

Normal editing commands should keep using the existing direct DeepSeek API planner.
An agent is not needed to change subtitle languages, logo, layout or context, or
submit a normal editing/publication request. This is the fastest, lowest-overhead
route. The configured `LAZYEDIT_AI_PROVIDER=deepseek` remains unchanged.

An operator can opt a workspace into `STUDIO_AGENT_URL` instead. This calls the
private planner container: AgInTi machine-run first, optional Codex exec fallback.
The fallback runs at most once on a runtime failure/timeout, never after a malformed
or unsupported plan. Neither route posts independently: Studio validates the
result, account capability, quota and immutable intent before its existing queue.
No fallback or retry replays a publication. Existing unknown dispatches still
require reconciliation. This integration is **planning only**, not an autonomous
live-code repair agent. Runtime completion is never evidence of publication.

## Isolation

- Separate non-root, read-only Docker container; all capabilities dropped,
  no-new-privileges, one active plan, at most eight HTTP connections.
- 768 MiB memory ceiling, one CPU, 96 process limit, 96 MiB temporary filesystem.
- Each request uses a fresh temporary HOME/workdir and deletes it afterwards.
- No media duplication, browser profile, project checkout, host HOME, SSH key,
  Docker socket, database credentials or personal Codex login mounted.
- AgInTi shell, files, web search, MCP, scouts, wrappers and auxiliary tools disabled.
  `--sandbox-mode host` means the **container**, never the workstation.
- Codex uses ephemeral read-only mode, shell disabled, web search disabled.
- Only dedicated provider API credentials and a separate service bearer are mounted.
  Personal ChatGPT/Codex login is not a multi-user service credential.
- Request/result limits 100 KB; 40-second AgInTi and 30-second Codex budgets;
  process groups killed on deadline, output overflow and exit.
- No prompt, response, raw provider diagnostic or credential logging.
- Loopback-only standalone port; hosted planner has no published port and is
  separated from the gateway and database networks.

The container has outbound network access for the model APIs. It is **not** an
outbound-firewall or microVM security boundary. Do not enable arbitrary shell/web
research on this service. A future tool-capable agent requires enforced egress
allowlists, scoped tool capabilities and separate per-task containers first.

## Build and standalone qualification

```sh
docker build -f deploy/agent/Dockerfile -t lazyedit-agent:local .
# A private directory outside Git, owned by the operator; files readable by uid 1000:
# agent_token: independent random bearer, >=32 characters
# deepseek_key: project-scoped API key
# codex_key: project-scoped Codex API key (empty disables usable fallback)
export STUDIO_AGENT_SECRETS=/private/lazyedit-agent-secrets
docker compose -f deploy/agent/compose.yaml up -d --no-build
```

Never put keys in command arguments, source files or images. The container has no
credentials until the operator mounts them. Pinned image packages are AgInTi
0.20.331 and Codex 0.162.1. Update deliberately and rerun qualification; the AgInTi
development checkout can have flags not present in the published package.

For a **test-only** Studio planner invocation, set:

```sh
export STUDIO_AGENT_URL=http://127.0.0.1:18992
export STUDIO_AGENT_TOKEN_FILE=/private/lazyedit-agent-secrets/agent_token
```

Without `STUDIO_AGENT_URL`, the current direct API behavior is unchanged. An
unavailable configured sandbox fails closed; it does not switch to a host agent.
Only health and planning endpoints exist, both require the bearer. Do not expose
this service through public LazyEdge routes. Test with synthetic input first,
then the existing Studio contract tests; never use a real publish for a smoke test.

## Whole app / migration

The app already has a multi-stage portable image in `deploy/hosted/Dockerfile`:
gateway, provisioner and isolated per-user editing/publisher workspace. Retain
these boundaries instead of combining every user's browsers and account state
into one container. `hosted/compose.mjs` owns the per-workspace topology.

To add the optional planner to a newly qualified workspace, set the operator's
`agentSandbox: true` and optional pinned `agentImage`. Supply files `agent_token`,
`agent_deepseek_key`, `agent_codex_key` in that workspace's protected bootstrap.
The worker receives only the agent bearer; provider secrets go to the planner.
The planner gets no workspace volume. Do not modify an acceptance-locked workspace.

For migration: drain/record pending editing intents and publication receipts;
stop dispatch on the old instance; make a consistent database backup and one
copy of its matching workspace volume; restore them with protected bootstrap
configuration and the pinned image on the new host. Preserve ownership IDs,
message IDs, database/queue journals and file paths. Verify isolated login,
upload, prepare, preview and receipt reconciliation before switching LazyEdge.
Keep the old dispatcher disabled to prevent duplicate posts. Never migrate the
owner's Pi profiles into other user workspaces. No such live migration is performed
by installing the optional planner.

See `deploy/hosted/README.md`, `references/studio/preparation-recovery.md` and
`references/studio/agent-mode.md` for the existing deployment/queue contracts.

## Tests

```sh
/home/lachlan/miniconda3/envs/lazyedit/bin/python -m pytest tests/test_agent_sandbox.py -q
node --test hosted/agent-compose.test.mjs studio/agent.test.mjs
```

These cover fixed tool policy, private environment, malformed-plan rejection,
bounded execution, fallback eligibility, cleanup, endpoint restrictions, no
additional containers in default mode, optional container isolation, and existing
owner/capability/idempotent queue behavior. A live provider canary is required
before activation; successful mocked fallback tests alone are not live qualification.

## Qualification result — 2026-10-15

**Not enabled in production.** Seven Python tests and nine Node contract tests
passed. The image built and both pinned CLI binaries started. Idle planner
measurement was approximately 58 MiB (768 MiB is its ceiling, not reserved usage).
The live synthetic AgInTi canary failed closed: `chatops --no-scs` still classified
the JSON interpretation contract as source/file correction and returned
`model_did_not_execute`. A plain natural-language rewrite of assignment examples
did not fix the broader execution-evidence misclassification. This belongs in
AgInTi's runtime, not a per-video prompt workaround. Do not activate this route
until an updated pinned package passes the same exact synthetic contract.

A dedicated Codex API key was not configured, so live Codex inference/fallback is
**not qualified**; CLI startup and deterministic fallback mechanics were tested.
No personal account credentials were borrowed. The disposable canary service is
removed after testing; the built image is retained. Existing direct DeepSeek,
hosted users, owner backend, Pi, media and queues are unchanged.
