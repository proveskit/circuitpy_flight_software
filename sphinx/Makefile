# Minimal makefile for Sphinx documentation

.PHONY: help clean html

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  clean     to clean up the generated files"

clean:
	@rm -rf _build

html:
	@sphinx-build -b html . _build/html
