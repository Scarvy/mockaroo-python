.PHONY: test clean

test:
	pytest

clean: clean-dist
	rm -rf __pycache__ .pytest_cache .mypy_cache ./**/__pycache__
	rm -f .coverage coverage.xml ./**/*.pyc
	rm -rf .tox

clean-dist:
	rm -rf dist mockaroo_python.egg-info