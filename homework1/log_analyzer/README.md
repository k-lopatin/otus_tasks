Для запуска скрипта выполнить команду:
python log_analyser.py --config=config.json
Где config.json - путь к файлу конфига.
Если не указать параметр --config то будут использованы параметры по умолчанию.

Конфиг указывается в формате json:
{
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./logs",
    "MONITORING_FILE": "./monitoring.log",
    "TS_FILE": "./log_analyser.ts"
}



Для запуска тестов необходимо выполнить команду:
python -m unittest tests.test_analyser