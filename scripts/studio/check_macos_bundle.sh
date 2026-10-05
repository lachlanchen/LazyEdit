#!/bin/bash
# Reject an incomplete universal Mac bundle before exporting or installing it.
set -euo pipefail
app="${1:?Supply the Mac app bundle}"
build="${2:?Supply the exact expected build}"
[[ "$build" =~ ^[0-9]+$ && -d "$app/Contents" && ! -L "$app" ]] || exit 2
plist="$app/Contents/Info.plist"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$plist")" == art.lazying.lazyedit ]]
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$plist")" == "$build" ]]
[[ "$(/usr/libexec/PlistBuddy -c 'Print :LSMinimumSystemVersion' "$plist")" == 12.0 ]]
executable=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$plist")
[[ -f "$app/Contents/MacOS/$executable" ]]
count=0
while IFS= read -r -d '' binary; do
    if [[ "$(file -b "$binary")" != *Mach-O* ]]; then continue; fi
    architectures=$(lipo -archs "$binary")
    if [[ " $architectures " != *" arm64 "* || " $architectures " != *" x86_64 "* ]]; then
        echo "Universal Mac bundle is missing an architecture: $binary ($architectures)" >&2
        exit 2
    fi
    count=$((count + 1))
done < <(find "$app/Contents" -type f -print0)
[[ "$count" -gt 0 ]]
codesign --verify --deep --strict "$app"
echo "Verified Studio $build: $count universal Mach-O binaries; Intel and Apple Silicon, macOS 12+."
