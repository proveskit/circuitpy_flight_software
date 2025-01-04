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
	python3 -m pytest FC_Board/tests

##@ Build

.PHONY: build
build: download-libraries ## Build the project, store the result in the artifacts directory
	mkdir -p artifacts
	rm -rf artifacts/FC_Board/
	cp -r FC_Board artifacts/FC_Board
	find artifacts/FC_Board -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf artifacts/FC_Board/tests
	zip -r artifacts/proves.zip artifacts/FC_Board

##@ Library Management

download-libraries: ## Download the required libraries
	pip3 install --requirement FC_Board/lib/requirements.txt --target FC_Board/lib --no-deps
	rm -rf FC_Board/lib/*.dist-info
