.PHONY: srpm

srpm:
	@set -eu; \
	if [ -z "$(spec)" ]; then \
		printf '%s\n' "error: spec is required (for example, spec=actionlint.spec)" >&2; \
		exit 2; \
	fi; \
	if [ -z "$(outdir)" ]; then \
		printf '%s\n' 'error: outdir is required' >&2; \
		exit 2; \
	fi; \
	if [ ! -f "$(spec)" ]; then \
		printf 'error: spec file not found: %s\n' "$(spec)" >&2; \
		exit 2; \
	fi; \
	mkdir -p "$(outdir)"; \
	if ! command -v spectool >/dev/null 2>&1; then \
		if command -v dnf5 >/dev/null 2>&1; then \
			dnf5 -y install rpmdevtools; \
		elif command -v dnf >/dev/null 2>&1; then \
			dnf -y install rpmdevtools; \
		else \
			printf '%s\n' 'error: spectool is missing and no dnf package manager is available' >&2; \
			exit 127; \
		fi; \
	fi; \
	spectool -g -C "$(CURDIR)" "$(spec)"; \
	rpmbuild -bs "$(spec)" \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(abspath $(outdir))"
