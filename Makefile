DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
FILE = docker/docker_compose.yml
APP_CONTAINER = forum_app
DB_CONTAINER = db

.PHONY: all
all:
	${DC} -f ${FILE} ${ENV} up --build -d

.PHONY: all-down
all-down:
	${DC} -f ${FILE} down

.PHONY: app
app:
	${DC} -f ${FILE} ${ENV} up -d ${APP_CONTAINER}

.PHONY: app-down
app-down:
	${DC} -f ${FILE} down ${APP_CONTAINER}

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} bash

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: app-test
app-test:
	${EXEC} ${APP_CONTAINER} python manage.py test

.PHONY: db
db:
	${DC} -f ${FILE} ${ENV} up -d ${DB_CONTAINER}

.PHONY: db-down
db-down:
	${DC} -f ${FILE} down ${DB_CONTAINER}

.PHONY: db-logs
db-logs:
	${LOGS} ${DB_CONTAINER} -f

.PHONY: status
status:
	${DC} -f ${FILE} ps