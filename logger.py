from functools import wraps
from datetime import datetime


def logger(old_function):
    log_file = 'main.log'

    @wraps(old_function)
    def new_function(*args, **kwargs):
        with open(log_file, 'a') as log:
            log.write(f'Дата: {datetime.now().strftime("%H:%M:%S %d.%m.%Y")}\n')
            log.write(f'Функция: {old_function.__name__}\n')
            log.write(f'Аргументы: {args}, {kwargs}\n')
            result = old_function(*args, **kwargs)
            log.write(f'Результат: {result}\n\n')

        return result

    return new_function
