class StreamStatsError(Exception):
    """Базовое исключение."""

class UnsupportedFormatError(StreamStatsError):
    """Формат входного файла не поддерживается."""

class InvalidEventError(StreamStatsError):
    """Событие не прошло валидацию."""

    def __init__(self, message: str, path: str | None = None, line_no: int | None = None):
        super().__init__(message)
        self.path = path
        self.line_no = line_no

    def __str__(self) -> str:
        base = super().__str__()
        if self.path and self.line_no:
            return f"{self.path}:{self.line_no}: {base}"
        return base

class InvalidTimestampError(InvalidEventError):
    """Неверная временная метка."""

class CLIConfigError(StreamStatsError):
    """Неверная конфигурация CLI."""