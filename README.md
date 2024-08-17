Пример ETL

Перый запуск:
```
make first_run
make up
```
После выполнения команды, дождаться сообщений об окончании миграций, и завершить вручную `Ctrl + C`:
```
alembic-init-source exited with code 0
alembic-init-target exited with code 0
airflow-init exited with code 0   <--- вот здесь можно завершить
```

После первого запуска, поднять можно так:
```
make up
```

[Web AirFlow](http://localhost:8080/)

Логин / пароль: `airflow` / `airflow`

