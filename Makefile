.PHONY: fmt
fmt:
	black .

.PHONY: test
test:
	pytest CircuitPy/FC_Board/tests
