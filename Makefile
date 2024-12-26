.PHONY: fmt
fmt:
	black .

.PHONY: test
test:
	pytest FC_Board/tests
