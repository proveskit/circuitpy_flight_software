.PHONY: all
all: .venv download-libraries pre-commit-install help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.venv: ## Create a virtual environment
	@echo "Creating virtual environment..."
	@$(MAKE) uv
	@$(UV) venv
	@$(UV) pip install --requirement pyproject.toml

.PHONY: download-libraries
download-libraries: .venv ## Download the required libraries
	@echo "Downloading libraries..."
	@$(UV) pip install --requirement lib/requirements.txt --target lib --no-deps --upgrade --quiet
	@rm -rf lib/*.dist-info
	@rm -rf lib/.lock

.PHONY: pre-commit-install
pre-commit-install: uv
	@echo "Installing pre-commit hooks..."
	@$(UVX) pre-commit install > /dev/null

.PHONY: fmt
fmt: pre-commit-install ## Lint and format files
	$(UVX) pre-commit run --all-files

.PHONY: test
test: .venv ## Run tests
	$(UV) run coverage run --rcfile=pyproject.toml -m pytest tests/unit
	@$(UV) run coverage html --rcfile=pyproject.toml > /dev/null
	@$(UV) run coverage xml --rcfile=pyproject.toml > /dev/null

BOARD_MOUNT_POINT ?= ""
VERSION ?= $(shell git tag --points-at HEAD --sort=-creatordate < /dev/null | head -n 1)

.PHONY: install
install: build ## Install the project onto a connected PROVES Kit use `make install BOARD_MOUNT_POINT=/my_board_destination/` to specify the mount point
ifeq ($(OS),Windows_NT)
	rm -rf $(BOARD_MOUNT_POINT)
	cp -r artifacts/proves/* $(BOARD_MOUNT_POINT)
else
	$(call rsync_to_dest,$(BOARD_MOUNT_POINT))
endif

.PHONY: clean
clean: ## Remove all gitignored files such as downloaded libraries and artifacts
	git clean -dfX

##@ Build

.PHONY: build
build: download-libraries ## Build the project, store the result in the artifacts directory
	@echo "Creating artifacts/proves"
	@mkdir -p artifacts/proves
	$(call rsync_to_dest,artifacts/proves/)
	@echo "__version__ = '$(VERSION)'" > artifacts/proves/version.py
	@echo "Creating artifacts/proves.zip"
	@zip -r artifacts/proves.zip artifacts/proves > /dev/null

define rsync_to_dest
	@if [ -z "$(1)" ]; then \
		echo "Issue with Make target, rsync destination is not specified. Stopping."; \
		exit 1; \
	fi

	@rsync -avh config.json artifacts/proves/version.py ./*.py ./lib --exclude='requirements.txt' --exclude='__pycache__' $(1) --delete --times --checksum
endef

##@ Build Tools
TOOLS_DIR ?= tools
$(TOOLS_DIR):
	mkdir -p $(TOOLS_DIR)

### Tool Versions
UV_VERSION ?= 0.5.24

UV_DIR ?= $(TOOLS_DIR)/uv-$(UV_VERSION)
UV ?= $(UV_DIR)/uv
UVX ?= $(UV_DIR)/uvx
.PHONY: uv
uv: $(UV) ## Download uv
$(UV): $(TOOLS_DIR)
	@test -s $(UV) || { mkdir -p $(UV_DIR); curl -LsSf https://astral.sh/uv/$(UV_VERSION)/install.sh | UV_INSTALL_DIR=$(UV_DIR) sh > /dev/null; }
