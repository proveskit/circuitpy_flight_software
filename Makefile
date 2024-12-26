.PHONY: fmt
fmt:
	black .

.PHONY: test
test:
	pytest Tests/unit_tests
