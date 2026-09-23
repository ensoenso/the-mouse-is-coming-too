#!/bin/zsh
set -euo pipefail

root_dir=${0:A:h:h}
cd "$root_dir"

private_path_pattern='/(Users|home)/[^/$]+/'
email_pattern='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
credential_pattern='(api[_-]?key|access[_-]?token|client[_-]?secret|password|private[_-]?key)[[:space:]]*[:=]'
research_pattern='(decode-obfuscator|dump-dotnet|asar-inspect|remote-debugging-port|findings\.md)'

search_args=(--hidden --glob '!.git/**' --glob '!build/**' \
  --glob '!The Mouse Is Coming Too/**' --glob '!dist/*.zip' \
  --glob '!tools/audit-public.sh')

failed=0
for pattern in "$private_path_pattern" "$email_pattern" "$credential_pattern" "$research_pattern"; do
  if rg -n -i "$pattern" . "${search_args[@]}"; then
    failed=1
  fi
done

if git ls-files -co --exclude-standard | rg '(^|/)(\.DS_Store|.*\.pyc)$'; then
  failed=1
fi

if (( failed )); then
  print -u2 "public-data audit failed"
  exit 1
fi

print "public-data audit passed"
