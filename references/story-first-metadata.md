# Story-First Metadata

For narrative videos, titles, descriptions and tags describe the characters,
events, relationships, setting and emotional payoff. Production notes provide
context; they are not publication copy. Labels such as AI-generated, 2D/3D,
model names and rendering details are omitted from story copy by default.

The shared policy applies to Chinese, English and Japanese metadata templates
and legacy generation entry points. Technical tutorials, making-of videos and
explicitly requested technical descriptions can still discuss their actual
subject. An AI robot can also be a character in a story. Native platform
declaration controls are separate and unchanged.

Templates are read for each metadata request, so the existing backend picks up
these template changes without a restart. A changed system prompt invalidates
the provider request cache. Existing published posts are not edited by this
change.

## Existing Prepared Videos

Regenerate metadata only through `POST /api/videos/{id}/metadata`, once per
metadata language, with the reviewed story context and `use_cache: false`.
Inspect the generated copy, then publish the existing verified subtitle/logo
master with `--no-process --no-correct-subtitles`. This avoids regenerating
video, changing subtitles or overwriting reviewed translations while repairing
descriptions. Check for an existing remote job before retrying a failed dispatch.

## Verification

`python -m pytest tests/test_metadata_story_copy.py` checks all three live
templates, both legacy entry points, policy idempotence, context preservation
and the distinction between story copy, technical topics and platform labels.
