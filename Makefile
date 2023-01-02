test:
	pytest tests/
fmt:
	isort .
	black .
style:
	isort --check --diff .
	black --check --diff .
	mypy -p sitegen
	pylint sitegen
