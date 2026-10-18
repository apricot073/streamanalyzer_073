# streamstats

Консольная утилита: читает события из файлов `.csv` и `.jsonl` и строит статистический отчет в `.json` и `.csv`.

# Установка
pip install -e .

pip install pytest ruff

# Использование
python -m streamstats analyze a.csv b.jsonl --output report.json

python -m streamstats analyze data.jsonl --format jsonl --skip-invalid

Формат либо определяется по расширению, либо задается через `--format`.

В конце можно добавить фильтры по уровню/источнику/времени событий, которые вы хотите исключить из отчета.

Время: --since (ISO 8601) --until (ISO 8601)

Источник: --source SOURCE

Уровень: --level {...}

# Формат события
Поля: `timestamp` (ISO 8601), `level` (DEBUG, INFO, WARNING, ERROR, CRITICAL),
`source` (непустая строка), `message` (строка).

Timestamp без часового пояса считается UTC.
