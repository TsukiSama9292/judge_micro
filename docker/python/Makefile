# Python OJ Runner Makefile

.PHONY: clean build test demo help test-ci test-squares test-advanced test-string test-factorial test-list test-error test-warning

# Default target
all: build

# Clean generated files
clean:
	@echo "Cleaning Python OJ Runner..."
	rm -f test_main.py
	rm -f function_result.txt
	rm -f result*.json
	rm -f user_backup_temp.py
	rm -f user_backup_demo.py
	rm -f user_backup_ci.py
	rm -f __pycache__/*.pyc
	rm -rf __pycache__
	@echo "Clean completed."

# Build target (Python doesn't need compilation, but we can validate syntax)
build:
	@echo "Building Python OJ Runner..."
	@echo "Validating harness.py syntax..."
	python3 -m py_compile harness.py
	@echo "Harness validation completed."
	@echo "Python OJ Runner is ready to use."

# Test with basic examples
test: build
	@echo "Testing Python OJ Runner..."
	
	@echo "Test 1: Basic functionality"
	python3 harness.py config.json result_test.json
	@if [ -f result_test.json ]; then \
		echo "✓ Basic test passed"; \
	else \
		echo "✗ Basic test failed"; \
	fi
	
	@echo "Test 2: List processing"
	cp user_list.py user.py
	python3 harness.py config_list.json result_list_test.json
	@if [ -f result_list_test.json ]; then \
		echo "✓ List test passed"; \
	else \
		echo "✗ List test failed"; \
	fi
	
	@echo "Test 3: Factorial calculation"
	cp user_factorial.py user.py
	python3 harness.py config_factorial.json result_factorial_test.json
	@if [ -f result_factorial_test.json ]; then \
		echo "✓ Factorial test passed"; \
	else \
		echo "✗ Factorial test failed"; \
	fi
	
	@echo "All tests completed."

# Individual test targets
test-squares: build
	@echo "Testing squares function..."
	@if [ -f user.py ]; then cp user.py user_backup_temp.py; fi
	cp user_squares.py user.py
	python3 harness.py config_squares.json result_squares.json
	@if [ -f user_backup_temp.py ]; then mv user_backup_temp.py user.py; fi

test-advanced: build
	@echo "Testing advanced list operations..."
	@if [ -f user.py ]; then cp user.py user_backup_temp.py; fi
	cp user_advanced.py user.py
	python3 harness.py config_advanced.json result_advanced.json
	@if [ -f user_backup_temp.py ]; then mv user_backup_temp.py user.py; fi

test-string: build
	@echo "Testing string manipulation..."
	@if [ -f user.py ]; then cp user.py user_backup_temp.py; fi
	cp user_string.py user.py
	python3 harness.py config_string.json result_string.json
	@if [ -f user_backup_temp.py ]; then mv user_backup_temp.py user.py; fi

test-factorial: build
	@echo "Testing factorial calculation..."
	@if [ -f user.py ]; then cp user.py user_backup_temp.py; fi
	cp user_factorial.py user.py
	python3 harness.py config_factorial.json result_factorial.json
	@if [ -f user_backup_temp.py ]; then mv user_backup_temp.py user.py; fi

test-list: build
	@echo "Testing list processing..."
	@if [ -f user.py ]; then cp user.py user_backup_temp.py; fi
	cp user_list.py user.py
	python3 harness.py config_list.json result_list.json
	@if [ -f user_backup_temp.py ]; then mv user_backup_temp.py user.py; fi

test-error: build
	@echo "Testing error handling..."
	@if [ -f user.py ]; then cp user.py user_backup_temp.py; fi
	cp user_error_test.py user.py
	python3 harness.py config_error_test.json result_error_test.json
	@if [ -f user_backup_temp.py ]; then mv user_backup_temp.py user.py; fi

test-warning: build
	@echo "Testing warning handling..."
	@if [ -f user.py ]; then cp user.py user_backup_temp.py; fi
	cp user_warning_test.py user.py
	python3 harness.py config_warning_test.json result_warning_test.json
	@if [ -f user_backup_temp.py ]; then mv user_backup_temp.py user.py; fi

# CI/CD specialized test (JSON format output)
test-ci: build
	@echo '{"test_suite": "Python OJ Microservice", "timestamp": "'$$(date -u +%Y-%m-%dT%H:%M:%SZ)'", "tests": ['
	@if [ -f user.py ]; then cp user.py user_backup_ci.py; fi; \
	failed=0; total=0; first=true; \
	for test in squares advanced string factorial list warning error; do \
		if [ "$$first" = "true" ]; then first=false; else echo ','; fi; \
		total=$$((total + 1)); \
		echo -n '  {"name": "'$$test'", '; \
		if [ "$$test" = "error" ]; then \
			$(MAKE) test-error >/dev/null 2>&1; error_exit=$$?; \
			if [ -f result_error_test.json ] && (grep -q '"status".*"ERROR"' result_error_test.json || grep -q '"status".*"RUNTIME_ERROR"' result_error_test.json || [ $$error_exit -ne 0 ]); then \
				echo '"status": "PASS", "expected": "error", "actual": "error"}'; \
			else \
				echo '"status": "FAIL", "expected": "error", "actual": "success"}'; failed=$$((failed + 1)); \
			fi; \
		else \
			if $(MAKE) test-$$test >/dev/null 2>&1; then \
				result_file="result_$$test.json"; \
				if [ "$$test" = "warning" ]; then result_file="result_warning_test.json"; fi; \
				if [ -f "$$result_file" ] && grep -q '"status".*"SUCCESS"' "$$result_file"; then \
					echo '"status": "PASS", "expected": "success", "actual": "success"}'; \
				else \
					echo '"status": "FAIL", "expected": "success", "actual": "error"}'; failed=$$((failed + 1)); \
				fi; \
			else \
				echo '"status": "FAIL", "expected": "success", "actual": "error"}'; failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ -f user_backup_ci.py ]; then mv user_backup_ci.py user.py; fi; \
	echo ''; \
	echo '], "summary": {'; \
	echo '  "total": '$$total','; \
	echo '  "passed": '$$((total - failed))','; \
	echo '  "failed": '$$failed','; \
	echo '  "success_rate": '$$((total > 0 ? (total - failed) * 100 / total : 0))'}}'

# Run demo
demo: build
	@echo "Running Python OJ Runner demo..."
	./demo.sh

# Show help
help:
	@echo "Python OJ Runner Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all          - Build the runner (default)"
	@echo "  build        - Validate Python syntax"
	@echo "  clean        - Remove generated files"
	@echo "  test         - Run basic tests"
	@echo "  test-ci      - CI/CD specialized test (JSON format output)"
	@echo "  demo         - Run full demonstration"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Individual test targets:"
	@echo "  test-squares   - Test squares function"
	@echo "  test-advanced  - Test advanced list operations"
	@echo "  test-string    - Test string manipulation"
	@echo "  test-factorial - Test factorial calculation"
	@echo "  test-list      - Test list processing"
	@echo "  test-error     - Test error handling (expected to fail)"
	@echo "  test-warning   - Test warning handling"
	@echo ""
	@echo "Usage:"
	@echo "  make [target]"
	@echo ""
	@echo "Examples:"
	@echo "  make build"
	@echo "  make test"
	@echo "  make test-ci"
	@echo "  make demo"
