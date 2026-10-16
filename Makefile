SHELL := /bin/bash

PACKAGES_DIR := $(CURDIR)/packages
OUTDIR ?= $(CURDIR)/dist/srpm
PACKAGE ?=

.PHONY: help list validate srpm

help:
	@printf '%s\n' \
	  'Targets:' \
	  '  make list' \
	  '  make validate' \
	  '  make srpm PACKAGE=<name> [OUTDIR=dist/srpm]'

list:
	@find "$(PACKAGES_DIR)" -mindepth 2 -maxdepth 2 -type f -name '*.spec' -printf '%h\n' \
	  | xargs -r -n1 basename | sort

validate:
	@./scripts/validate.py

srpm:
	@test -n "$(PACKAGE)" || { echo 'PACKAGE is required' >&2; exit 2; }
	@test -f "$(PACKAGES_DIR)/$(PACKAGE)/$(PACKAGE).spec" || { echo "Unknown package: $(PACKAGE)" >&2; exit 2; }
	@$(MAKE) -C "$(PACKAGES_DIR)/$(PACKAGE)" -f ../../.copr/Makefile srpm \
	  spec="$(PACKAGE).spec" outdir="$(OUTDIR)"
