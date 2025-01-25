dev:
	docker-compose -f dev.docker-compose.yaml up

stop:
	docker-compose -f dev.docker-compose.yaml down