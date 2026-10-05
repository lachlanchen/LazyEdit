#!/bin/bash
# Run on the established signing Mac. Only this app's archive is built/exported.
set -euo pipefail
umask 077
root="${LAZYEDIT_MAC_ROOT:-$HOME/Projects/LazyEditStudio}"
helper_dir=$(cd "$(dirname "$0")" && pwd)
build="${LAZYEDIT_BUILD_NUMBER:?Set the exact Mac candidate build}"
[[ "$build" =~ ^[0-9]+$ ]] || exit 2
private="$HOME/.config/echomind/apple"
keychain="$HOME/Library/Keychains/lazyedit-studio-release.keychain-db"
installer_keychain="${LAZYEDIT_INSTALLER_KEYCHAIN:-$HOME/Library/Keychains/landn-release.keychain-db}"
password=$(tr -d '\r\n' < "$private/release-keychain.pass")
previous=$(security list-keychains -d user)
cleanup() {
  printf '%s\n' "$previous" | xargs security list-keychains -d user -s
  security lock-keychain "$keychain" || true
}
trap cleanup EXIT
security unlock-keychain -p "$password" "$keychain"
security unlock-keychain -p "$password" "$installer_keychain"
unset password
security list-keychains -d user -s "$keychain" "$installer_keychain" "$HOME/Library/Keychains/login.keychain-db"
mkdir -p "$root/release" "$HOME/Library/MobileDevice/Provisioning Profiles" "$HOME/Library/Developer/Xcode/UserData/Provisioning Profiles"
profile_info=$(mktemp "$root/release/.mac-profile.XXXXXX")
options=$(mktemp "$root/release/.mac-export.XXXXXX")
trap 'rm -f "$profile_info" "$options"; cleanup' EXIT
security cms -D -i "$root/LazyEditMac.provisionprofile" > "$profile_info"
uuid=$(/usr/libexec/PlistBuddy -c 'Print :UUID' "$profile_info")
name=$(/usr/libexec/PlistBuddy -c 'Print :Name' "$profile_info")
[[ "$(/usr/libexec/PlistBuddy -c 'Print :Entitlements:com.apple.application-identifier' "$profile_info")" == Q8M2S2FY77.art.lazying.lazyedit ]]
[[ "$(/usr/libexec/PlistBuddy -c 'Print :TeamIdentifier:0' "$profile_info")" == Q8M2S2FY77 ]]
cp "$root/LazyEditMac.provisionprofile" "$HOME/Library/MobileDevice/Provisioning Profiles/$uuid.provisionprofile"
cp "$root/LazyEditMac.provisionprofile" "$HOME/Library/Developer/Xcode/UserData/Provisioning Profiles/$uuid.provisionprofile"
cat > "$options" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
<key>method</key><string>app-store-connect</string>
<key>destination</key><string>export</string>
<key>signingStyle</key><string>manual</string>
<key>teamID</key><string>Q8M2S2FY77</string>
<key>signingCertificate</key><string>Apple Distribution</string>
<key>installerSigningCertificate</key><string>3rd Party Mac Developer Installer: LazyingArt LLC (Q8M2S2FY77)</string>
<key>manageAppVersionAndBuildNumber</key><false/>
<key>provisioningProfiles</key><dict><key>art.lazying.lazyedit</key><string>$name</string></dict>
</dict></plist>
EOF
cd "$root/ios/App"
# Distribution signing generates fresh signature/profile files during export.
# Keep the release directory private while giving installed bundle files the
# ordinary 0644/0755 permissions Apple requires.
chmod 700 "$root/release"
umask 022
archive="$root/release/LazyEditStudio-macOS-$build.xcarchive"
if [[ "${LAZYEDIT_EXPORT_ONLY:-0}" != 1 ]]; then
if [[ -e "$archive" ]]; then echo 'Preserve the existing candidate archive; use LAZYEDIT_EXPORT_ONLY=1 to resume export.' >&2; exit 2; fi
xcodebuild -project App.xcodeproj -scheme StudioNative -configuration Release \
  -destination 'generic/platform=macOS,variant=Mac Catalyst' \
  -archivePath "$archive" -derivedDataPath "$root/release/MacStoreDerivedData" -jobs 2 \
  archive CURRENT_PROJECT_VERSION="$build" DEVELOPMENT_TEAM=Q8M2S2FY77 \
  IPHONEOS_DEPLOYMENT_TARGET=15.0 MACOSX_DEPLOYMENT_TARGET=12.0 \
  ARCHS='arm64 x86_64' ONLY_ACTIVE_ARCH=NO CODE_SIGN_STYLE=Manual \
  CODE_SIGN_IDENTITY='Apple Distribution' "PROVISIONING_PROFILE_SPECIFIER=$name" \
  "CODE_SIGN_ENTITLEMENTS=$root/ios/App/App/StudioMac.entitlements" \
  "OTHER_CODE_SIGN_FLAGS=--keychain $keychain" \
  OTHER_LDFLAGS='$(inherited) -weak_framework SwiftUICore' COMPILER_INDEX_STORE_ENABLE=NO \
  > "$root/release/mac-store-$build-archive.log" 2>&1
fi
app="$archive/Products/Applications/App.app"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Contents/Info.plist")" == art.lazying.lazyedit ]]
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$app/Contents/Info.plist")" == "$build" ]]
bash "$helper_dir/check_macos_bundle.sh" "$app" "$build"
# Installed resources must be readable by ordinary users. The release parent
# directory stays private; credential/export-option files remain mode 0600.
chmod -R a+rX "$app"
xcodebuild -exportArchive -archivePath "$archive" -exportOptionsPlist "$options" \
  -exportPath "$root/release/mac-store-export-$build" > "$root/release/mac-store-$build-export.log" 2>&1
shasum -a 256 "$root/release/mac-store-export-$build/App.pkg"
