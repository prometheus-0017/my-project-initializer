[pytest]
testpaths = tests
pythonpath = .
addopts = --cov=app --cov=config --cov-report=term-missing --cov-fail-under=70
