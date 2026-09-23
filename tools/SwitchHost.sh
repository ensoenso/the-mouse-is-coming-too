#!/bin/zsh
contents_dir=${0:A:h:h}
host=$(/usr/libexec/PlistBuddy -c 'Print :TMCTHost' "$contents_dir/Info.plist")
exec /usr/bin/python3 "$contents_dir/Resources/app_launcher.py" "$host"
