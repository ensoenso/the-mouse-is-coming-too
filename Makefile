.PHONY: test apps dist audit clean

test:
	/usr/bin/python3 -m unittest -v

apps:
	zsh tools/make-launcher-apps.sh

dist:
	zsh tools/package-release.sh

audit:
	zsh tools/audit-public.sh

clean:
	rm -rf build
