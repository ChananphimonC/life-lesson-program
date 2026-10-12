"""Pipeline-specific exceptions.

Kept as a flat set of exception types (no exception hierarchy beyond a
common base) so callers can catch `PipelineError` broadly or a specific
stage's error narrowly, per REQUIREMENTS.md's "reject rather than
silently repair" and error-handling expectations.
"""


class PipelineError(Exception):
    """Base class for all life-lesson pipeline errors."""


class ScriptGenerationError(PipelineError):
    """Raised when the Gemini API call for script generation fails."""


class ScriptValidationError(PipelineError):
    """Raised when a generated script does not match the required JSON schema."""


class TTSError(PipelineError):
    """Raised when speech synthesis for a script block fails."""


class VideoAssemblyError(PipelineError):
    """Raised when FFmpeg video assembly fails."""


class ConfigurationError(PipelineError):
    """Raised when required configuration (e.g. an API key) is missing."""
