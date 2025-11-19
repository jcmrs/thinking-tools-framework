"""Processing layer for template rendering and validation.

This module implements Layer 3 (Processing) of the five-layer architecture.
Provides secure template rendering and validation functionality.
"""

from cogito.processing.renderer import TemplateRenderer, TemplateRenderError
from cogito.processing.validator import (
    ParameterValidationError,
    ParameterValidator,
    SchemaValidator,
    ToolSpecValidationError,
)

__all__ = [
    "TemplateRenderer",
    "TemplateRenderError",
    "ParameterValidator",
    "ParameterValidationError",
    "SchemaValidator",
    "ToolSpecValidationError",
]
