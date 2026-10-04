#!/usr/bin/env python
"""Build the shared LazyEdit Studio launcher icon.

This asset is the application icon only. It must never replace the configured
video watermark/logo used by the publishing pipeline.
"""
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "figs/app-icon/lazyedit-studio-icon-v2.png"


def rasterize(source: Path, destination: Path, size: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "convert",
            str(source),
            "-resize",
            f"{size}x{size}",
            "-alpha",
            "off",
            f"PNG24:{destination}",
        ],
        check=True,
    )


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"missing canonical app icon: {SOURCE}")

    rasterize(SOURCE, ROOT / "studio/web/icon.png", 1024)

    for density, size in (
        ("mdpi", 48),
        ("hdpi", 72),
        ("xhdpi", 96),
        ("xxhdpi", 144),
        ("xxxhdpi", 192),
    ):
        for name in ("ic_launcher", "ic_launcher_round"):
            rasterize(
                SOURCE,
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
    )
    rasterize(
        SOURCE,
        ROOT / "mobile/ios/App/App/Assets.xcassets/StudioMark.imageset/StudioMark.png",
        256,
    )

    # Desktop assets reuse the same approved master, without changing the artwork.
    mac = ROOT / "mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset"
    for size in (16, 32, 64, 128, 256, 512, 1024):
        rasterize(SOURCE, mac / f"StudioMac-{size}.png", size)
    from PIL import Image
    windows = ROOT / "mobile/windows/Assets/Studio.ico"
    windows.parent.mkdir(parents=True, exist_ok=True)
    Image.open(SOURCE).convert("RGB").save(windows, sizes=[(n, n) for n in (16, 32, 48, 64, 128, 256)])
    for name, size in (("Logo44", 44), ("Logo150", 150), ("StoreLogo", 50)):
        rasterize(SOURCE, ROOT / f"mobile/windows/msix/Assets/{name}.png", size)


if __name__ == "__main__":
    main()
