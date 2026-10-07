#!/usr/bin/env python
"""Build the shared LazyEdit Studio launcher icon.

This asset is the application icon only. It must never replace the configured
video watermark/logo used by the publishing pipeline.
"""
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "figs/app-icon/lazyedit-studio-icon-v2.png"
ROUNDED_SOURCE = ROOT / "figs/app-icon/lazyedit-studio-icon-v2-rounded.png"


def rasterize(source: Path, destination: Path, size: int, *, opaque=False, inset=0) -> None:
    """Preserve rounded alpha except for Apple's system-masked iOS app icon."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    inner = size - 2 * inset
    command = ["convert", str(source), "-resize", f"{inner}x{inner}"]
    if inset:
        command += ["-background", "none", "-gravity", "center", "-extent", f"{size}x{size}"]
    if opaque:
        command += ["-alpha", "off", f"PNG24:{destination}"]
    else:
        command += [f"PNG32:{destination}"]
    subprocess.run(command, check=True)


def main() -> None:
    if not SOURCE.is_file() or not ROUNDED_SOURCE.is_file():
        raise SystemExit("missing full-bleed or rounded canonical app icon")

    rasterize(ROUNDED_SOURCE, ROOT / "studio/web/icon.png", 1024)

    for density, size in (
        ("mdpi", 48),
        ("hdpi", 72),
        ("xhdpi", 96),
        ("xxhdpi", 144),
        ("xxxhdpi", 192),
    ):
        for name in ("ic_launcher", "ic_launcher_round"):
            rasterize(
                ROUNDED_SOURCE,
                ROOT / f"mobile/android/app/src/main/res/mipmap-{density}/{name}.png",
                size,
            )

    # Keep the existing adaptive-icon resource structure, but use the same
    # vivid artwork rather than the old unrelated panda foreground.
    for density, size in (
        ("mdpi", 108),
        ("hdpi", 162),
        ("xhdpi", 216),
        ("xxhdpi", 324),
        ("xxxhdpi", 432),
    ):
        rasterize(
            SOURCE,
            ROOT
            / f"mobile/android/app/src/main/res/mipmap-{density}/ic_launcher_foreground.png",
            size,
        )

    # Native iOS icon and in-app Studio mark use the same approved artwork.
    rasterize(
        SOURCE,
        ROOT / "mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/StudioRibbon-v2.png",
        1024,
        opaque=True,
    )
    rasterize(
        ROUNDED_SOURCE,
        ROOT / "mobile/ios/App/App/Assets.xcassets/StudioMark.imageset/StudioMark.png",
        256,
    )

    # Desktop assets reuse the same approved master, without changing the artwork.
    mac = ROOT / "mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset"
    for size in (16, 32, 64, 128, 256, 512, 1024):
        rasterize(ROUNDED_SOURCE, mac / f"StudioMac-{size}.png", size, inset=max(1, size // 16))
    from PIL import Image
    windows = ROOT / "mobile/windows/Assets/Studio.ico"
    windows.parent.mkdir(parents=True, exist_ok=True)
    Image.open(ROUNDED_SOURCE).convert("RGBA").save(windows, sizes=[(n, n) for n in (16, 32, 48, 64, 128, 256)])
    for name, size in (("Logo44", 44), ("Logo150", 150), ("StoreLogo", 50)):
        rasterize(ROUNDED_SOURCE, ROOT / f"mobile/windows/msix/Assets/{name}.png", size)


if __name__ == "__main__":
    main()
