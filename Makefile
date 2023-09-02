coverage:
	coverage run -m pytest tests/
	coverage report

lint:
	pylint src/
