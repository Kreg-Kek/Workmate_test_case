# Workmate_test_case

Тестовое задание для собеседование в кампанию Workmate: скрипт для обработки .csv файлов, который выводит отчёт по медианной сумме трат студентов на кофе.

Команды для тестовых запусков с 1 файлом и с несколькими:

1. python script.py --files math.csv --report median-coffee
2. python script.py --files math.csv physics.csv programming.csv --report median-coffee

Запуск тестов:
python -m pytest --cov=script --cov-report=term-missing
Покрытие 86%
