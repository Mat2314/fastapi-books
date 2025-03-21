# FastAPI books

The side project of a web application to store information about books, their authors and regular users as readers.

Authors can add their books into the app. Delete and update them.

Users can browse books and save them to favorites.

The aim of this project is to have a go at the following technologies:
- FastAPI and SQLAlchemy
- PostgreSQL (testing some advanced queries on a big database)
- Angular (frontend simple AF)
- Cloud Run (deployment of the application on Google Cloud run as a Serverless solution)
- Cloud SQL (communicate with the prod DB in the cloud)
- Artifacts registry in Google Cloud
- Testing app (backend in pytest | E2E tests with Selenium )
- CI/CD with github actions
...

Later on:
- Kubernetes (Google Kubernetes Engine to try how it works)


## Run Dev Environment
### FastAPI
It is suggested to run it locally in the VSCode with the debugger. Configure the debugger specifying the following values in `launch.json` file:
```
"args": [
    "main:app",
    "--reload"
],
```


### Docker containers
Using `Makefile` run the following command to setup containers for development:
```
make dev
```

Then check data for pgadmin service in docker-compose file and go to `http://localhost:$(SPECIFIED_PORT_IN_DOCKER_COMPOSE)` and use credentials from the file to access the panel.

To connect to the server in pgadmin use the data from docker-compose file.
Example:
```
Host name/address: [docker_service_name]
Port: 5432 (or other if specified)
Maintenance database: fabooks (check in docker-compose)
Password: mypassword (check in docker-compose)
```

## Running dev
To run the app locally in dev mode run the following command. It will start the postgres database and pgadmin service. Migration will be run automatically.
```
make dev
```

Then you can run your debugger in VSCode and the api should be available under `http://localhost:8000`

To browse the database go to `http://localhost:8999` and use credentials from the file docker-compose file to access the panel.

Alternatively you can enter docker container and run psql command to connect to the database.

```
docker exec -it db bash
psql -U mat -d fabooks
```


## Running tests
To run backend tests locally run:
```
make test
```

To run backend tests with coverage run:
```
make test_coverage
```

To run frontend tests locally run:
```
make test_frontend
```

To run frontend tests with coverage run:
```
make test_frontend_coverage
```


## CI/CD pipeline
We use Google Cloud and Github Actions to run the CI/CD pipeline



## Run in Production
...