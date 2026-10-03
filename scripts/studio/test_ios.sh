#!/bin/bash
# Dedicated simulator only. Reuse existing Xcode; no production keys are changed.
set -euo pipefail
umask 077
root="$HOME/Projects/LazyEditStudio"
device="${STUDIO_TEST_SIMULATOR:?Supply the dedicated Studio simulator ID}"
credentials="${STUDIO_TEST_CREDENTIALS:?Supply the protected QA account file}"
selection="${STUDIO_TEST_SELECTION:-StudioUITests/StudioUITests/testMemberPrivateLibraryAndLoginDesktop}"
receipt="${STUDIO_TEST_RECEIPT:-$root/release/qa-current.xcresult}"
[[ "$device" =~ ^[A-Fa-f0-9-]{36}$ ]] || exit 2
[[ -f "$credentials" && ! -L "$credentials" ]] || exit 2
[[ ! -e "$receipt" ]] || { echo 'Preserve existing test receipt; select a new path.' >&2; exit 2; }
cd "$root/ios/App"
derived="$root/release/SimulatorDerivedData"
entitlements=$(mktemp "$root/release/simulator-entitlements.XXXXXX")
trap 'rm -f "$entitlements"' EXIT
# Let Xcode embed simulated entitlements in the simulator binary. Re-signing
# the finished bundle with device entitlements instead makes AMFI reject it.
# No production profile/key, Keychain fallback or system trust change is used.
cat > "$entitlements" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>application-identifier</key><string>Q8M2S2FY77.art.lazying.lazyedit</string>
<key>keychain-access-groups</key><array><string>Q8M2S2FY77.art.lazying.lazyedit</string></array>
</dict></plist>
PLIST
settings=(CODE_SIGNING_ALLOWED=YES CODE_SIGN_IDENTITY=- "CODE_SIGN_ENTITLEMENTS=$entitlements" "STUDIO_TEST_CREDENTIALS=$credentials")
xcodebuild -project App.xcodeproj -scheme StudioNative \
  -destination "platform=iOS Simulator,id=$device" -derivedDataPath "$derived" \
  "${settings[@]}" -only-testing:"$selection" build-for-testing
app="$derived/Build/Products/Debug-iphonesimulator/App.app"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Info.plist")" == art.lazying.lazyedit ]]
codesign --verify --deep --strict "$app"
xcodebuild -project App.xcodeproj -scheme StudioNative \
  -destination "platform=iOS Simulator,id=$device" -derivedDataPath "$derived" \
  -resultBundlePath "$receipt" "${settings[@]}" \
  -only-testing:"$selection" test-without-building
