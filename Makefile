help: ## Помощь
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

up: ## Поднять docker compose
	docker-compose -f docker-compose.yml up

first_run: ## Выполнить первый запуск
	docker compose -f docker-compose.yml -f docker-compose.init.yml build alembic-init-db-target
	docker compose -f docker-compose.yml -f docker-compose.init.yml build alembic-init-db-source
	echo "AIRFLOW_UID=$$(id -u)" > .env
	docker compose -f docker-compose.yml -f docker-compose.init.yml up \
		db-target \
		alembic-init-db-target \
		db-source \
		alembic-init-db-source \
		airflow-db \
		airflow-init
