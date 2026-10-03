# Workspace login and interface qualification

The hosted workspace serves upload, editing and publication. Generation controls
and owner Nutstore controls are absent from the invited-user PWA. Native iOS and
Android retain primary native screens; advanced editing and platform login use
the secondary authenticated browser. The original owner backend and Pi are not
restarted or enrolled in another tunnel by this work.

## Browser restrictions and the automation conflict

Chromium's `DeveloperToolsAvailability=2` looked like a suitable restriction,
but live testing showed that it also stops publisher CDP page commands. Browser
metadata still answered, while a simple page evaluation timed out. That setting
must not be used in an automated publishing browser.

The replacement keeps publisher CDP private, uses kiosk browser windows and
Openbox grabs for developer-tool/menu shortcuts and right-click. Only the
platform sites and necessary authentication/captcha origins are permitted by
the navigation policy. Guest profiles, profile creation, extensions, incognito,
printing, browser sync and manual file-selection dialogs are disabled. The X
desktop contains no panel, terminal, launcher or application menu. Closing its
last browser leaves a blank desktop; a platform button reopens its saved profile.

Actual private-workspace checks confirmed:

- CDP page evaluation and automation file upload work.
- An unrelated HTTPS website, a local file and a data page return
  `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
- F12, Ctrl+Shift+I/J/C, Alt+F and F10 opened no developer-tools target.
- Shipinhao's login page still loads in the fitted private desktop.

These checks establish the intended login interface, not a claim that Chromium
or a container kernel cannot have vulnerabilities. Keep admission invite-only,
fixed operator templates, CPU/memory/process limits, private volumes, and no
Docker socket in either gateway or user workspace. This remains a controlled
pilot; billing and broader capacity are separate readiness items.

## Mobile controls and traffic

The viewer offers Fit, 150%, 200% and 300% zoom with local scrolling, using the
same framebuffer and stream. Its fallback cursor is clipped to the desktop
rectangle. Keep QR visible makes a memory-only still image and disconnects;
tap the QR area to enlarge it. Hidden screens and five minutes without input
disconnect the stream. There is one viewer lease per workspace, bounded startup
and connection timeouts, and explicit reconnect rather than retry loops.

## Languages and account cache

The interface dictionaries contain 339 entries in English, simplified/traditional
Chinese, Japanese, Korean, Vietnamese, Arabic, French, Spanish, German and
Russian. `scripts/studio/sync_interface.py` validates every key and copies exact
JSON bytes into both native resource directories. `translate_interface.py`
translates missing public interface strings only; it never sends media, QR codes,
passwords or private account data. Incomplete JSON responses are not saved.

The PWA obtains its cache namespace from an authenticated, no-store
`/studio-context.js`. Cached selections and upload state are separate for each
account/workspace and never fall back to old shared browser storage. Interface
language itself is non-private and can be shared across the login screen.
Arabic uses right-to-left layout. Generated content and provider errors keep
their original language when they are not interface dictionary entries.

## Sample, notifications and promotion

Only the owner's explicitly authorized Vancouver sample is seeded. Its source
hash is checked before import, its host mount is read-only, and one canonical
editable source is retained per private workspace. A reflink is attempted before
copying. Repeated startup reuses the file and DB row; sample ownership is mapped
to that workspace for linked clients. No personal library, queue or platform
profile is imported.

Native login notifications are opt-in and generic: no QR, credentials or video
title is exposed on the lock screen. Dedupe and tap routing are scoped to the
account/workspace. Polling stops when the app leaves the foreground. This release
does not claim APNs/FCM delivery while the app is closed.

`scripts/studio/promote_cells.py` checks both queues before a fixed-image rolling
promotion. It records prior Compose/config files and preserves every persistent
volume. It does not restart the owner backend, Pi, ingress or personal tunnel.
Use `promote_hosted.py` separately for immutable Studio ingress releases.

## Store pricing and remaining release work

On 2026-10-04 the actual Google Play app-pricing page permitted Free → Paid
because production had not yet published. USD 0.99 was saved and read back;
Play calculated regional prices. Apple likewise confirmed a USD 0.99 base price
schedule via the app-specific helper. This is a configured download price,
not a claim of production availability.

Monthly subscription intent remains USD 2.99 / 14.99 / 29.89. Purchase activation
requires defined benefits, exact provider products, native purchase/restore,
server verification, refund handling, account deletion and purchase QA. Paid
download credit must use verified store evidence, never a client assertion.
OAuth buttons must remain unavailable until their own provider configuration
and account-linking flow are qualified. Review submission must accurately
describe these capabilities and access boundaries.
