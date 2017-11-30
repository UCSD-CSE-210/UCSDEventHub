TESTS=tests/unit tests/functional

test:
	py.test -v $(TESTS)

cov:
	py.test --cov-config=.coveragerc --cov-report=html --cov=. tests/unit tests/functional

all:test cov