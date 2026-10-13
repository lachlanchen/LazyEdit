#!/bin/bash
# Install one verified local-QA Mac bundle; no signing or TCC settings change.
set -euo pipefail
umask 077
helper_dir=$(cd "$(dirname "$0")" && pwd)
archive="${1:?Supply the exact QA ZIP}"
build="${2:?Supply the expected build number}"
expected="${3:?Supply the verified SHA-256}"
[[ "$build" =~ ^[0-9]+$ && "$expected" =~ ^[a-f0-9]{64}$ ]] || exit 2
[[ -f "$archive" && ! -L "$archive" ]] || exit 2
[[ "$(shasum -a 256 "$archive" | cut -d ' ' -f1)" == "$expected" ]]
destination="$HOME/Applications/LazyEditStudio-review-$build"
[[ ! -e "$destination" ]] || { echo 'Preserve existing review installation.' >&2; exit 2; }
staging=$(mktemp -d "$HOME/Applications/.lazyedit-review.XXXXXX")
trap 'rm -rf "$staging"' EXIT
ditto -x -k "$archive" "$staging"
app="$staging/LazyEdit Studio.app"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Contents/Info.plist")" == art.lazying.lazyedit ]]
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$app/Contents/Info.plist")" == "$build" ]]
bash "$helper_dir/check_macos_bundle.sh" "$app" "$build"
# Stop only this project's superseded review executable, after verification.
while read -r pid; do
  command=$(ps -p "$pid" -o comm= || true)
  if [[ "$command" == "$HOME/Applications/LazyEditStudio-review-"*/LazyEdit Studio.app/Contents/MacOS/LazyEdit Studio ]]; then
    kill "$pid"
  fi
done < <(pgrep -f '/LazyEditStudio-review-[0-9]+/LazyEdit Studio.app/Contents/MacOS/LazyEdit Studio' || true)
mv "$staging" "$destination"
# Freshly extracted local QA bundles can lack a Launch Services registration
# on newer macOS even though strict signature verification succeeds. Register
# this exact bundle; do not reset the shared database or change Gatekeeper.
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$destination/LazyEdit Studio.app"
open "$destination/LazyEdit Studio.app"
echo "Launched verified Studio build $build; local QA signature, not notarized."
