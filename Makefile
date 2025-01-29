dev:
	docker-compose -f dev.docker-compose.yaml up

stop:
	docker-compose -f dev.docker-compose.yaml down

test:
	cd api/ && pytest

test_coverage:
	cd api/ && pytest --cov=. --cov-report=term-missing --cov-fail-under=90 tests/ 