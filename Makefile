.PHONY: fmt
fmt:
	pre-commit run --all-files

.PHONY: test
test:
	pytest FC_Board/tests

.PHONY: build
build:
	mkdir -p artifacts
	zip -r artifacts/proves.zip FC_Board
