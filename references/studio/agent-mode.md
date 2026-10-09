# Studio Agent mode

Agent is a chat entry point to the existing LazyEdit pipeline. It does not run a
second renderer, publisher, shell agent or social browser. Media stays in the
same workspace and uses the same publication queue as the editor.

## Using it

1. Open **Agent** in authenticated Studio. Attach a video from the device or
   choose an existing Studio video. The attachment uses the existing resumable
   upload and registers one source; chat stores only its video ID.
2. Describe the video, reference story, names, subtitle languages, layout and
   platforms. Omitted options inherit the current Studio defaults. These are
   one-time overrides; website preferences are not rewritten.
3. Leave **Publish after editing** off to get an edited preview. An account with
   publishing enabled can turn it on before sending to authorize processing
   followed by publication. Questions and unclear instructions do not start jobs.
4. Read the resolved settings and real progress below the message. Return to the
   conversation after leaving the app. Login/verification requirements are also
   shown in Activity using the existing notification/QR flow.

Example:

> We had lunch at 莲香西域. I said “你们这个很厉害啊，谢谢你们”. Correct recognition
> using this context and the full conversation. Korean on the bottom, Chinese
> above it, then Japanese and English. No lift. Use the existing logo at the
> top right. Publish to Shipinhao, Instagram, YouTube and Douyin.

For a Musia recording:

> This is a recording of my song player. Use the supplied lyrics and song story
> for metadata. No burned subtitles; keep the existing logo top right. Prepare
> a preview first.

For an additional platform after a completed run:

> Use completed run 7 unchanged and publish it to Xiaohongshu only.

The reuse path verifies the saved run and platform history. It does not regenerate
the video or silently post again to previously used channels.

## Editing behaviour

- Full-conversation subtitle correction remains in the normal pipeline. User
  context is evidence, not permission to invent speech or force a script onto
  the audio. The polished transcript is used for translation and rendering.
- Subtitle languages are represented bottom-to-top. The normal renderer owns
  grammar colours, Japanese readings, Chinese pinyin and supported restoration.
  Requests for other languages use the shared backend language catalogue.
- Logo uses the configured existing asset. No subtitles and no logo are separate
  choices. Portrait sources keep background fill disabled by physical geometry.
- Metadata describes the actual video, not internal workflow or the whole script.
- Preparation, covers, rendering, packaging and social publication use the same
  backend functions as the native composer. No new platform credentials are used.

## Contracts and implementation

`studio/agent.mjs` stores owner-bound conversations and immutable message intents
in the existing private authentication database. `studio/agent_plan.py` interprets
instructions with the configured text provider/model. It has no tools, filesystem
lookup, web research, code editing or publication authority. It reads configuration
without importing the GPU/backend application and does not cache or log prompts.

The planner sees the bound video's title, current choices, available run labels,
and bounded prior conversation. It does not watch the video. The established
transcription/correction/caption pipeline examines the media after submission.
Ask for external research separately, then paste its relevant context into chat.

The authenticated worker routes are:

| Route | Purpose |
| --- | --- |
| `GET /v1/studio/agent/chats` | Own conversations and capabilities |
| `POST /v1/studio/agent/chats` | Bind `videoId`, optional stable chat `id` |
| `GET /v1/studio/agent/chats/{id}` | Conversation, receipt, process/job/attention status |
| `POST /v1/studio/agent/chats/{id}/messages` | Interpret and submit one instruction |

Message example (first-party Studio browser/native session):

```json
{
  "id": "a-stable-client-generated-uuid",
  "message": "Prepare this video with no lift and the existing top-right logo.",
  "action": "prepare",
  "language": "en"
}
```

Send `Idempotency-Key: agent-<message.id>`. Allowed actions are `prepare` and
`publish`. A message ID is 16–80 ASCII letters/digits/underscores/hyphens and
cannot be reused with different text, action, language or conversation. Text is
limited to 16,000 characters, a conversation to 100 messages, and an owner to six
new messages/minute. The model request has a 90-second process deadline.

Native iOS/Mac Catalyst and Android screens use their existing cookie-based
Studio login, resumable upload and private pending-request storage. PWA drafts
use the existing account/workspace storage namespace. Linked third-party bearer
clients continue using the existing preparation and reviewed-publication API;
chat does not bypass that contract. The unauthenticated local workstation UI
links to the authenticated Agent page instead of creating another public API.

## Reliability and separation

1. Persist the original message before interpretation. Persist the validated
   interpretation before any pipeline mutation. Repeated sends use the same ID.
2. The shared composer lock/queue checks prevent conflicting requests for the
   same video. Different videos still enter the normal serialized publish queue.
3. Persist the existing intent marker before backend dispatch. If the outcome is
   unknown, hold the message for reconciliation; never replay publication under
   another ID. A durable receipt can repair an interrupted chat response.
4. `submitted` means accepted by the backend, **not published**. Completion and
   login attention come from the queue/preparation receipts. The planner's prose
   is not displayed as execution status: a real smoke test said “submitted” before
   dispatch despite its instructions, so executable turns use deterministic status.
5. A definite pre-dispatch rejection releases the pending client request. Quota
   and permission failures cannot get stuck forever behind a saved message.
6. Hosted publication policy, media ownership, same-origin checks and source-minute
   metering apply to chat. The gateway injects trusted quota headers on message
   routes; a client cannot turn itself into an unlimited owner or Pi user.
7. Actual platform login or verification may still need the owner. Agent does not
   bypass it, automatically repair source code, or repeatedly re-post failed jobs.

## Validation and rollout

Run `node --test studio/*.test.mjs hosted/*.test.mjs`. Regression coverage includes
idempotency, ambiguous dispatch, receipt recovery, permissions, forged quota
headers, ordinary-member isolation, completed-run reuse, unsupported model fields,
polished context/ruby defaults and portrait fill prevention. Browser QA uses a
small synthetic attachment and a fake backend, never a real social publisher.

Native validation: Android debug build, Swift type-check with the installed iOS
SDK; web TypeScript and production export. Native source validation does not mean
a new TestFlight/Play build is installed or released.

`scripts/studio/promote_agent.py --webdist temp/agent-webdist --activate` stages an
immutable **owner adapter + web** release, checks the owner queue and recent
submissions, and restarts only that adapter with rollback on health failure. It
does not restart the Python editor, AutoPublish Pi, gateway, tunnel or private
workers. Hosted workers use the normal image promotion after their acceptance
locks are released. Never remove another client's lock to enable chat.

Keep private deployment receipts and coordination notes under
`Nutstore Files/OneTimeSync/LazyEdit/`; no credentials, conversations or media in Git.
