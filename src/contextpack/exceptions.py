"""Custom exceptions."""

from __future__ import annotations


class ContextPackError(Exception):
    """Base error raised by ContextPack."""


class ConfigError(ContextPackError):
    """Raised when configuration cannot be loaded or parsed."""


class RepositoryError(ContextPackError):
    """Raised when a target repository is invalid."""


class OutputError(ContextPackError):
    """Raised when output cannot be written safely."""
