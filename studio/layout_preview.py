#!/usr/bin/env python
"""Read-only geometry from the same implementation used by the renderer."""
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[3])
from lazyedit.portrait_blurfill import (  # noqa: E402
    probe_display_resolution, sanitize_portrait_blurfill,
    _foreground_geometry, _scaled_height,
)

path = sys.argv[1]
config = sanitize_portrait_blurfill(json.loads(sys.argv[2]))
width, height = probe_display_resolution(path)
portrait = height > width
result = {"width": width, "height": height, "portrait": portrait, "fill": False}
if config["enabled"] and not portrait:
    fg_width, top = _foreground_geometry(path, config)
    fg_height = _scaled_height(width, height, fg_width)
    result.update(fill=True, outputWidth=config["width"], outputHeight=config["height"],
                  foregroundWidth=fg_width, foregroundHeight=fg_height,
                  top=top, bottom=config["height"] - fg_height - top)
print(json.dumps(result))
