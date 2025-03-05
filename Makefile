dev:
	docker compose -f dev.docker-compose.yaml up -d
	sleep 2
	$(MAKE) migrate

stop:
	docker compose -f dev.docker-compose.yaml down

create_test_db:
	docker compose -f dev.docker-compose.yaml exec db psql -U mat -d fabooks -c "CREATE DATABASE test_db;" || true

test: 
	@TESTING=true; \
	docker compose -f dev.docker-compose.yaml up -d; \
	sleep 2; \
	$(MAKE) create_test_db; \
	$(MAKE) migrate; \
	cd api/ && pytest; \
	$(MAKE) stop


test_coverage: 
	@TESTING=true; \
	docker compose -f dev.docker-compose.yaml up -d; \
	sleep 2; \
	$(MAKE) create_test_db; \
	$(MAKE) migrate; \
	cd api/ && pytest --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=90 tests/; \
	$(MAKE) stop

migrate:
	cd api/ && alembic upgrade head

revision:
	cd api/ && alembic revision --autogenerate -m "$(message)"

help-populate:
	cd api/ && python -m scripts.manage populate --help

populate:
	cd api/ && python -m scripts.manage populate $(records)

flush_db:
	cd api/ && python -m scripts.manage clean

# In case no records count is provided, show help
ifndef records
populate:
	@echo "Usage: make populate records=<number_of_records>"
endif



# In case no message is provided, show help
ifndef message
revision:
	@echo "Usage: make revision message='your migration message'"
endif