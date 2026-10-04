#!/bin/bash
# Run on the existing Mac with mobile/ios synced to ~/Projects/LazyEditStudio/ios.
# Native Mac Catalyst; local QA signature only, not a notarized public installer.
set -euo pipefail
umask 077
root="$HOME/Projects/LazyEditStudio"
build_number="${LAZYEDIT_BUILD_NUMBER:?Supply the exact expected build number}"
[[ "$build_number" =~ ^[0-9]+$ ]] || exit 2
cd "$root/ios/App"
xcodebuild -project App.xcodeproj -scheme StudioNative -configuration Release \
  -destination 'generic/platform=macOS,variant=Mac Catalyst' \
  -derivedDataPath "$root/release/MacDerivedData" \
  IPHONEOS_DEPLOYMENT_TARGET=15.0 MACOSX_DEPLOYMENT_TARGET=12.0 \
  ARCHS='arm64 x86_64' ONLY_ACTIVE_ARCH=NO CODE_SIGNING_ALLOWED=NO \
  CURRENT_PROJECT_VERSION="$build_number" \
  OTHER_LDFLAGS='$(inherited) -weak_framework SwiftUICore' \
  build > "$root/release/mac-build.log" 2>&1
app="$root/release/MacDerivedData/Build/Products/Release-maccatalyst/App.app"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Contents/Info.plist")" == art.lazying.lazyedit ]]
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$app/Contents/Info.plist")" == "$build_number" ]]
codesign --force --deep --sign - "$app"
codesign --verify --deep --strict "$app"
architectures=$(lipo -archs "$app/Contents/MacOS/App")
[[ " $architectures " == *" arm64 "* && " $architectures " == *" x86_64 "* ]]
output="$root/release/LazyEditStudio-macOS-${build_number}.zip"
ditto -c -k --sequesterRsrc --keepParent "$app" "$output"
shasum -a 256 "$output"
