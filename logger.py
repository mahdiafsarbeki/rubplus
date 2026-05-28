"""
Logging System for RubPlus - Clean & Professional
"""

from datetime import datetime
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
    
    def _write(self, level_name: str, message: str, fix: Optional[str] = None):
        if self.level.value >= getattr(LogLevel, level_name).value:
            print(f"[{level_name}] {message}")
            if fix:
                print(f"[FIX] {fix}")
        
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | {level_name} | {message}\n")
                if fix:
                    f.write(f"FIX: {fix}\n")
    
    def startup(self, version: str):
        if not self._version_shown:
            print(f"RubPlus v{version}")
            self._version_shown = True
    
    def connected(self):
        self._write("INFO", "Connected to Rubika server")
    
    def success(self):
        self._write("INFO", "Bot started successfully")
    
    def info(self, message: str):
        self._write("INFO", message)
    
    def warning(self, message: str, fix: Optional[str] = None):
        self._write("WARNING", message, fix)
    
    def error(self, message: str, fix: Optional[str] = None):
        self._write("ERROR", message, fix)