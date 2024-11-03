import logging
from logging.handlers import RotatingFileHandler
from enum import Enum
import json
import os
from .config import executor
from pathlib import Path

"""
NOTE
log记录这块在程序开始时会执行该py文件4次，会重置实例，没弄明白原因，也没有采用单例化的模式，直接把初始化写在了文件结尾
logger自身维持了锁，不用担心同步问题
"""
# Logger instance
logger = logging.getLogger("Logger")


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class CustomRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        files = [f for f in os.listdir('.') if f.endswith('.json')]
        numbers = []
        for f in files:
            try:
                num = int(f.split('.')[0])
                numbers.append(num)
            except ValueError:
                pass
        if numbers:
            self.counter = max(numbers) + 1
        else:
            self.counter = 1

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # 修改这里，加上正确的路径
        new_name = os.path.join("../log_file", f"{self.counter}.json")
        self.counter += 1
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, new_name)
        self.mode = 'w'
        self.stream = self._open()


class JsonFormatter(logging.Formatter):
    def format(self, record):
        custom_func_name = record.__dict__.get('custom_funcName', 'unknown')
        log_dict = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "funcName": custom_func_name,
            "lineno": record.lineno
        }
        return json.dumps(log_dict)


def set_log_level(level: LogLevel):
    global logger
    logger.setLevel(level.value)


def limit_file_quality(path: str, max_size, backup_count: int):
    global logger
    fh = CustomRotatingFileHandler(filename=path, maxBytes=max_size, backupCount=backup_count)
    fh.setFormatter(JsonFormatter())
    set_log_level(LogLevel.INFO)
    logger.addHandler(fh)


def init_logger_setting(in_path, in_max_size, in_backup_count):
    global logger
    limit_file_quality(in_path, in_max_size, in_backup_count)
    logging_message(LogLevel.INFO, "logger handle changed", init_logger_setting.__qualname__)
    print("logger init")


def logging_message(level: LogLevel,
                    message: str,
                    func_name: str):
    global logger
    if level == LogLevel.DEBUG:
        logger.debug(message, extra={"custom_funcName": func_name})
    elif level == LogLevel.INFO:
        logger.info(message, extra={"custom_funcName": func_name})
    elif level == LogLevel.WARNING:
        logger.warning(message, extra={"custom_funcName": func_name})
    elif level == LogLevel.ERROR:
        logger.error(message, extra={"custom_funcName": func_name})
    elif level == LogLevel.CRITICAL:
        logger.critical(message, extra={"custom_funcName": func_name})
    else:
        logger.error("can't find the level in logLevel")


async def logging_by_thread(level: LogLevel,
                            message: str,
                            func_name: str):
    executor.submit(logging_message, level, message, func_name)


# logger init
init_logger_setting(in_path=Path(__file__).parent.parent / "log_file/1.json",
                    in_max_size=32 * 1024,
                    in_backup_count=50)
