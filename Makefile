.PHONY: all
all: download-libraries help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: fmt
fmt: ## Lint and format files
	pre-commit run --all-files

.PHONY: test
test: ## Run tests
	python3 -m pytest tests/unit

##@ Build

.PHONY: build
build: download-libraries ## Build the project, store the result in the artifacts directory
	rm -rf artifacts/proves/
	mkdir -p artifacts/proves
	cp config.json artifacts/proves/
	cp ./*.py artifacts/proves/
	find ./lib -type d -name '__pycache__' -prune -o -type f -print | cpio -pdm artifacts/proves/
	zip -r artifacts/proves.zip artifacts/proves

##@ Library Management

download-libraries: ## Download the required libraries
	@echo "Downloading libraries..."
	@pip3 install --requirement lib/requirements.txt --target lib --no-deps --upgrade --quiet
	@rm -rf lib/*.dist-info
