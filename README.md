# streamstats

Консольная утилита: читает события из файлов `.csv` и `.jsonl` и строит статистический отчет.

## Установка
```pip install -e .```

```pip install pytest ruff```

## Использование
```python -m streamstats analyze a.csv b.jsonl --output report.json```

```python -m streamstats analyze data.json --format jsonl --skip-invalid```

Формат либо определяется по расширению, либо задается через `--format`. 

По умолчанию отчет выводится в терминал в формате JSON, но еще его можно записать в файл `.json` или `.csv`, тогда в в `--output` указывается название и расширение.

В аргументы можно в любом порядке добавить фильтры по уровню/источнику/времени событий, которые попадут в отчет.

Время: `--since` TIMESTAMP `--until` TIMESTAMP

Источник: `--source` SOURCE

Уровень: `--level` {...}

## Формат события
Поля: `timestamp` (ISO 8601), `level` (DEBUG, INFO, WARNING, ERROR, CRITICAL), `source` (непустая строка), `message` (строка).

Timestamp без часового пояса считается UTC.
