import os
import json
from enum import Enum
from src.config import executor

path = "../../config.json"

init_data = {'doc_num': 0,
             'task_num': 0,
             'user_num': 0}


class Key(Enum):
    doc_num = "doc_num"
    task_num = "task_num"
    user_num = "user_num"


def flush_config_data(data):
    with open(path, 'a') as f:
        json.dump(data, f)


def data_generator():
    while True:
        for i in range(10):
            key, incre_num = yield
            init_data[key] += incre_num
            yield init_data[key]
        executor.submit(flush_config_data, init_data)


generator = data_generator()
next(generator)


def init_config_file():
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump(init_data, f)
    else:
        data = None
        with open(path, 'r') as f:
            data = json.load(f)
        for key in init_data.keys():
            init_data[key] = data[key]


def increment_value(key: Key, increment_num: int):
    return generator.send((key.value, increment_num))


def close_generator():
    flush_config_data(init_data)
    generator.close()


init_config_file()
