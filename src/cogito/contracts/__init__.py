"""Contracts layer: Protocol definitions for architectural boundaries.

Defines formal interfaces using Python's typing.Protocol to enforce
the five-layer architecture and enable compile-time type checking.
"""

from cogito.contracts.layer_protocols import (
    IntegrationProtocol,
    KnowledgeGraphProtocol,
    OrchestrationProtocol,
    ProcessingProtocol,
    SchemaValidationProtocol,
    StorageProtocol,
    ToolRegistryProtocol,
    UIProtocol,
    ValidationProtocol,
)

__all__ = [
    "UIProtocol",
    "OrchestrationProtocol",
    "ToolRegistryProtocol",
    "ProcessingProtocol",
    "ValidationProtocol",
    "SchemaValidationProtocol",
    "StorageProtocol",
    "KnowledgeGraphProtocol",
    "IntegrationProtocol",
]
