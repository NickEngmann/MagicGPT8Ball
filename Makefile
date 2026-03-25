.PHONY: test clean

test:
	pytest test/ -v --tb=short

clean:
	find test -name "*.pyc" -delete
	find test -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find test -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
