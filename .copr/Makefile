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
	spectool -g -C "$(CURDIR)" "$(spec)"; \
	rpmbuild -bs "$(spec)" \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(abspath $(outdir))"
