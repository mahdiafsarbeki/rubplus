"""Small, dependency-free logging helper for RubPlus."""

import logging
from enum import Enum
from typing import Optional


class LogLevel(Enum):
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


class RubPlusLogger:
    def __init__(self, level: LogLevel = LogLevel.INFO, log_file: Optional[str] = None):
        self.level = level
        self.log_file = log_file
        self._version_shown = False
        self._logger = logging.getLogger(f"rubplus.{id(self)}")
        self._logger.propagate = False
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        stream = logging.StreamHandler()
        stream.setLevel(self._python_level())
        stream.setFormatter(formatter)
        self._logger.addHandler(stream)
        if log_file:
            try:
                handler = logging.FileHandler(log_file, encoding="utf-8")
                handler.setLevel(logging.DEBUG)
                handler.setFormatter(formatter)
                self._logger.addHandler(handler)
            except OSError as exc:
                self._logger.warning("Cannot open log file %s: %s", log_file, exc)

    def _python_level(self):
        return {
            LogLevel.ERROR: logging.ERROR,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.INFO: logging.INFO,
            LogLevel.DEBUG: logging.DEBUG,
        }.get(self.level, logging.INFO)

    def _write(self, level_name: str, message: str, fix: Optional[str] = None):
        method = getattr(self._logger, level_name.lower(), self._logger.info)
        method(message)
        if fix:
            method("Suggestion: %s", fix)

    def startup(self, version: str):
        if not self._version_shown:
            self._logger.info("RubPlus v%s", version)
            self._version_shown = True

    def connected(self):
        self.info("Connected to Rubika API")

    def success(self):
        self.info("Bot started successfully")

    def info(self, message: str):
        self._write("INFO", message)

    def warning(self, message: str, fix: Optional[str] = None):
        self._write("WARNING", message, fix)

    def error(self, message: str, fix: Optional[str] = None):
        self._write("ERROR", message, fix)

    def debug_log(self, message: str):
        self._write("DEBUG", message)

    def close(self):
        for handler in list(self._logger.handlers):
            handler.close()
            self._logger.removeHandler(handler)
