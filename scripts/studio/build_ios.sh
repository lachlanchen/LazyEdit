#!/bin/bash
# Run on the existing Mac after syncing mobile/ios into ~/Projects/LazyEditStudio/ios.
set -euo pipefail
umask 077
root="$HOME/Projects/LazyEditStudio"
build_number="${LAZYEDIT_BUILD_NUMBER:-3}"
[[ "$build_number" =~ ^[0-9]+$ ]] || exit 2
private="$HOME/.config/echomind/apple"
keychain="$HOME/Library/Keychains/lazyedit-studio-release.keychain-db"
password=$(tr -d '\r\n' < "$private/release-keychain.pass")
previous=$(security list-keychains -d user)
cleanup() {
  # Restore only the prior search list; preserve every other project's keychain.
  printf '%s\n' "$previous" | xargs security list-keychains -d user -s
  security lock-keychain "$keychain" || true
}
trap cleanup EXIT
if [ ! -f "$keychain" ]; then
 security create-keychain -p "$password" "$keychain"
 security unlock-keychain -p "$password" "$keychain"
 security import "$private/AppleRootCA.cer" -k "$keychain" -T /usr/bin/codesign >/dev/null
 security import "$private/AppleWWDRCAG3.cer" -k "$keychain" -T /usr/bin/codesign >/dev/null
 security import "$private/EchoMindDistribution.p12" -k "$keychain" -P "$password" -x -T /usr/bin/codesign -T /usr/bin/security >/dev/null
fi
security unlock-keychain -p "$password" "$keychain"
security set-keychain-settings -lut 14400 "$keychain"
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$password" "$keychain" >/dev/null
security list-keychains -d user -s "$keychain" "$HOME/Library/Keychains/login.keychain-db"
mkdir -p "$HOME/Library/MobileDevice/Provisioning Profiles" "$root/release"
cp "$root/LazyEdit.mobileprovision" "$HOME/Library/MobileDevice/Provisioning Profiles/0a68cf60-c0b8-4e11-b8c0-4440e346a8cc.mobileprovision"
cd "$root/ios/App"
xcodebuild -project App.xcodeproj -scheme StudioNative -configuration Release -destination generic/platform=iOS -archivePath "$root/release/LazyEditStudio-${build_number}.xcarchive" -derivedDataPath "$root/release/DerivedData" archive DEVELOPMENT_TEAM=Q8M2S2FY77 CODE_SIGN_STYLE=Manual CODE_SIGN_IDENTITY='Apple Distribution' PROVISIONING_PROFILE_SPECIFIER='LazyEdit Studio App Store 1' "OTHER_CODE_SIGN_FLAGS=--keychain $keychain" COMPILER_INDEX_STORE_ENABLE=NO > "$root/release/archive.log" 2>&1
archive_app="$root/release/LazyEditStudio-${build_number}.xcarchive/Products/Applications/App.app"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$archive_app/Info.plist")" == art.lazying.lazyedit ]]
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$archive_app/Info.plist")" == "$build_number" ]]
xcodebuild -exportArchive -archivePath "$root/release/LazyEditStudio-${build_number}.xcarchive" -exportOptionsPlist "$root/ExportOptions.plist" -exportPath "$root/release/export-${build_number}" > "$root/release/export.log" 2>&1
codesign --verify --deep --strict "$root/release/LazyEditStudio-${build_number}.xcarchive/Products/Applications/App.app"
shasum -a 256 "$root/release/export-${build_number}/App.ipa"
