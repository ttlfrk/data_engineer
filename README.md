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

Запрос для витрины (после запуска дага):
```sql
SELECT
    sat_course.s_title AS "Курс",
    sat_stream.s_name AS "Поток",
    CASE
        WHEN sat_stream.s_is_open THEN 'Открыт'
        ELSE 'Закрыт'
    END AS "Набор",
    sat_stream_module.s_title AS "Модуль",
    sat_stream_module_lesson.s_title AS "Занятие",
    sat_stream_module_lesson.s_start_at AS "Начало",
    sat_stream_module_lesson.s_end_at AS "Конец"
/* Курсы */
FROM
    data_vault.hub_course AS hub_course
INNER JOIN data_vault.sat_course AS sat_course ON
    sat_course.course_hash_key = hub_course.hash_key
    AND sat_course.is_active = TRUE
/* Потоки */
INNER JOIN data_vault.link_course_stream AS link_course_stream ON
    link_course_stream.course_hash_key = hub_course.hash_key
INNER JOIN data_vault.sat_stream AS sat_stream ON
    sat_stream.stream_hash_key = link_course_stream.stream_hash_key
    AND sat_stream.is_active = TRUE
INNER JOIN data_vault.hub_stream AS hub_stream ON
    hub_stream.hash_key = link_course_stream.stream_hash_key
/* Модули */
INNER JOIN data_vault.link_stream_stream_module AS link_stream_stream_module ON
    link_stream_stream_module.stream_hash_key = hub_stream.hash_key
INNER JOIN data_vault.sat_stream_module AS sat_stream_module ON
    sat_stream_module.stream_module_hash_key = link_stream_stream_module.stream_module_hash_key
    AND sat_stream_module.is_active = TRUE
INNER JOIN data_vault.hub_stream_module AS hub_stream_module ON
    hub_stream_module.hash_key = link_stream_stream_module.stream_module_hash_key
/* Уроки */
INNER JOIN data_vault.link_stream_module_stream_module_lesson AS link_stream_module_stream_module_lesson ON
    link_stream_module_stream_module_lesson.stream_module_hash_key = hub_stream_module.hash_key
INNER JOIN data_vault.sat_stream_module_lesson AS sat_stream_module_lesson ON
    sat_stream_module_lesson.stream_module_lesson_hash_key = link_stream_module_stream_module_lesson.stream_module_lesson_hash_key
    AND sat_stream_module_lesson.is_active = TRUE
ORDER BY
    sat_course.s_title,
    sat_stream.s_name,
    sat_stream_module.s_title,
    sat_stream_module.s_order_in_stream ASC,
    sat_stream_module_lesson.s_title
```

