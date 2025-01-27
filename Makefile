.PHONY: all
all: venv download-libraries pre-commit-install help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

ifeq ($(OS),Windows_NT)
BIN_DIR := venv/Scripts
PYTHON := $(shell which python)
VENV_PYTHON := $(BIN_DIR)/python.exe
else
BIN_DIR := venv/bin
PYTHON := python3
VENV_PYTHON := $(BIN_DIR)/python
endif

ACTIVATE_VENV := . $(BIN_DIR)/activate;

venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv venv
	@$(VENV_PYTHON) -m pip install --upgrade pip --quiet
	@$(VENV_PYTHON) -m pip install --requirement requirements.txt --quiet

.PHONY: download-libraries
download-libraries: venv ## Download the required libraries
	@echo "Downloading libraries..."
	@$(VENV_PYTHON) -m pip install --requirement lib/requirements.txt --target lib --no-deps --upgrade --quiet
	@rm -rf lib/*.dist-info

.PHONY: pre-commit-install
pre-commit-install: venv
	@echo "Installing pre-commit hooks..."
	@$(ACTIVATE_VENV) pre-commit install > /dev/null

.PHONY: fmt
fmt: pre-commit-install ## Lint and format files
	$(ACTIVATE_VENV) pre-commit run --all-files

.PHONY: test
test: venv ## Run tests
	$(ACTIVATE_VENV) $(PYTHON) -m pytest tests/unit

BOARD_MOUNT_POINT ?= ""

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
	@echo "Creating artifacts/proves.zip"
	@zip -r artifacts/proves.zip artifacts/proves > /dev/null

define rsync_to_dest
	@if [ -z "$(1)" ]; then \
		echo "Issue with Make target, rsync destination is not specified. Stopping."; \
		exit 1; \
	fi
	@rsync -avh config.json ./*.py ./lib --exclude='requirements.txt' --exclude='__pycache__' $(1) --delete
endef
