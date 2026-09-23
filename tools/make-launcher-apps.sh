#!/bin/zsh
set -euo pipefail

root_dir=${0:A:h:h}
destination_dir=${1:-"$root_dir/The Mouse Is Coming Too"}
version=$(<"$root_dir/VERSION")
mkdir -p "$destination_dir"

for slot in 1 2 3; do
  app="$destination_dir/Switch to Host $slot.app"
  mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources"
  cp "$root_dir/tools/launcher-Info.plist" "$app/Contents/Info.plist"
  cp "$root_dir/app_launcher.py" "$app/Contents/Resources/app_launcher.py"
  cp "$root_dir/plugin_service.py" "$app/Contents/Resources/plugin_service.py"
  cp "$root_dir/tools/SwitchHost.sh" "$app/Contents/MacOS/SwitchHost"
  chmod 755 "$app/Contents/MacOS/SwitchHost"
  /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier org.themouseiscomingtoo.host$slot" \
    "$app/Contents/Info.plist"
  /usr/libexec/PlistBuddy -c "Set :CFBundleName Switch to Host $slot" \
    "$app/Contents/Info.plist"
  /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $version" \
    "$app/Contents/Info.plist"
  /usr/libexec/PlistBuddy -c "Add :TMCTHost integer $((slot - 1))" \
    "$app/Contents/Info.plist"
  /usr/bin/codesign --force --sign - "$app"
done
