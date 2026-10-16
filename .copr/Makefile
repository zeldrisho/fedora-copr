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
	install_pkgs() { \
		if command -v dnf5 >/dev/null 2>&1; then \
			dnf5 -y install "$$@"; \
		elif command -v dnf >/dev/null 2>&1; then \
			dnf -y install "$$@"; \
		else \
			printf 'error: cannot install %s: no dnf package manager is available\n' "$$*" >&2; \
			exit 127; \
		fi; \
	}; \
	if ! command -v spectool >/dev/null 2>&1; then \
		install_pkgs rpmdevtools; \
	fi; \
	if grep -Eq '%\{?(gometa|goprep|go_vendor)' "$(spec)" \
		&& ! rpm -q --quiet go-rpm-macros go-vendor-tools; then \
		install_pkgs go-rpm-macros go-vendor-tools; \
	fi; \
	spectool -g -C "$(CURDIR)" "$(spec)"; \
	rpmbuild -bs "$(spec)" \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(abspath $(outdir))"
