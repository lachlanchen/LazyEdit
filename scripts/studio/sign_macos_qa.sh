#!/bin/bash
# Re-sign a copy of the exact candidate with an app-owned development identity.
# The store archive remains immutable. The supplied profile must include this Mac.
set -euo pipefail
umask 077
root="${LAZYEDIT_MAC_ROOT:-$HOME/Projects/LazyEditStudio}"
build="${LAZYEDIT_BUILD_NUMBER:?Supply the candidate build}"
identity="${LAZYEDIT_QA_IDENTITY:?Supply the app-owned development identity hash}"
[[ "$build" =~ ^[0-9]+$ && "$identity" =~ ^[A-Fa-f0-9]{40}$ ]] || exit 2
profile="$HOME/.config/lazyedit-studio/qa-signing/MacQA.provisionprofile"
keychain="$HOME/Library/Keychains/lazyedit-studio-release.keychain-db"
source="$root/release/LazyEditStudio-macOS-$build.xcarchive/Products/Applications/App.app"
destination="$root/release/MacQA$build/App.app"
[[ ! -e "$destination" || "${LAZYEDIT_QA_RESUME:-0}" == 1 ]] || { echo 'Preserve existing QA candidate; explicit QA resume is required.' >&2; exit 2; }
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$source/Contents/Info.plist")" == "$build" ]]
mkdir -p "$(dirname "$destination")"
if [[ ! -e "$destination" ]]; then ditto "$source" "$destination"; fi
cmp "$source/Contents/MacOS/App" "$destination/Contents/MacOS/App"
cp "$profile" "$destination/Contents/embedded.provisionprofile"
entitlements=$(mktemp "$root/release/.qa-entitlements.XXXXXX")
previous=$(security list-keychains -d user)
cleanup() {
  rm -f "$entitlements"
  printf '%s\n' "$previous" | xargs security list-keychains -d user -s
  security lock-keychain "$keychain"
}
trap cleanup EXIT
codesign -d --entitlements :- "$source" > "$entitlements" 2>/dev/null
/usr/libexec/PlistBuddy -c 'Set :get-task-allow true' "$entitlements"
password=$(tr -d '\r\n' < "$HOME/.config/echomind/apple/release-keychain.pass")
security unlock-keychain -p "$password" "$keychain"
unset password
security list-keychains -d user -s "$keychain" "$HOME/Library/Keychains/login.keychain-db"
codesign --force --deep --sign "$identity" --keychain "$keychain" \
  --entitlements "$entitlements" --generate-entitlement-der "$destination"
chmod -R a+rX "$destination"
codesign --verify --deep --strict "$destination"
open "$destination"
echo "Launched native Studio $build with a registered-device QA signature."
