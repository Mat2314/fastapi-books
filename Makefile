dev:
	docker-compose -f dev.docker-compose.yaml up

stop:
	docker-compose -f dev.docker-compose.yaml down

test:
	cd api/ && pytest

test_coverage:
	cd api/ && pytest --cov=. --cov-report=term-missing --cov-report=xml --cov-fail-under=90 tests/ 

migrate:
	cd api/ && alembic upgrade head

revision:
	cd api/ && alembic revision --autogenerate -m "$(message)"

# In case no message is provided, show help
ifndef message
revision:
	@echo "Usage: make revision message='your migration message'"
endif