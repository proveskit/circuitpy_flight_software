.PHONY: fmt
fmt:
	pre-commit run --all-files

.PHONY: test
test:
	pytest FC_Board/tests
