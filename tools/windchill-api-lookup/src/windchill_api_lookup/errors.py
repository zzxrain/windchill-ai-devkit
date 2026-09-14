"""Stable errors shared by the CLI and future query adapters."""


class ApiLookupError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}
