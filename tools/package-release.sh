#!/bin/zsh
set -euo pipefail

root_dir=${0:A:h:h}
version=$(<"$root_dir/VERSION")
build_dir="$root_dir/build/release"
dist_dir="$root_dir/dist"
archive="$dist_dir/the-mouse-is-coming-too-$version-macos.zip"
checksum="$dist_dir/SHA256SUMS"

if [[ "$build_dir" != "$root_dir/build/release" ]]; then
  print -u2 "refusing unexpected build directory: $build_dir"
  exit 1
fi

rm -rf "$build_dir"
mkdir -p "$build_dir" "$dist_dir"
/bin/zsh "$root_dir/tools/make-launcher-apps.sh" "$build_dir"
cp "$root_dir/INSTALL.md" "$build_dir/INSTALL.md"
cp "$root_dir/LICENSE" "$build_dir/LICENSE"

rm -f "$archive" "$checksum"
(
  cd "$build_dir"
  /usr/bin/zip -X -q -r "$archive" \
    "Switch to Host 1.app" \
    "Switch to Host 2.app" \
    "Switch to Host 3.app" \
    INSTALL.md LICENSE
)
(
  cd "$dist_dir"
  /usr/bin/shasum -a 256 "${archive:t}" > "$checksum"
)
