"""Unit tests for Protocol conformance.

Tests that implementations correctly conform to their declared protocols,
enforcing the five-layer architecture contracts.
"""

import pytest

from cogito.contracts.layer_protocols import (
    KnowledgeGraphProtocol,
    OrchestrationProtocol,
    ProcessingProtocol,
    SchemaValidationProtocol,
    StorageProtocol,
    ToolRegistryProtocol,
    ValidationProtocol,
)


class TestOrchestrationProtocolConformance:
    """Test that orchestration layer implementations conform to OrchestrationProtocol."""

    def test_tool_executor_conforms_to_orchestration_protocol(self) -> None:
        """Test that ToolExecutor conforms to OrchestrationProtocol."""
        from cogito.orchestration.executor import ToolExecutor

        executor = ToolExecutor()
        assert isinstance(executor, OrchestrationProtocol)

    def test_tool_registry_conforms_to_registry_protocol(self) -> None:
        """Test that ToolRegistry conforms to ToolRegistryProtocol."""
        from cogito.orchestration.registry import ToolRegistry

        registry = ToolRegistry()
        assert isinstance(registry, ToolRegistryProtocol)

    def test_executor_has_execute_method(self) -> None:
        """Test that ToolExecutor has execute method with correct signature."""
        from cogito.orchestration.executor import ToolExecutor

        executor = ToolExecutor()
        assert hasattr(executor, "execute")
        assert callable(executor.execute)

    def test_executor_has_execute_by_name_method(self) -> None:
        """Test that ToolExecutor has execute_by_name method."""
        from cogito.orchestration.executor import ToolExecutor

        executor = ToolExecutor()
        assert hasattr(executor, "execute_by_name")
        assert callable(executor.execute_by_name)

    def test_registry_has_discover_tools_method(self) -> None:
        """Test that ToolRegistry has discover_tools method."""
        from cogito.orchestration.registry import ToolRegistry

        registry = ToolRegistry()
        assert hasattr(registry, "discover_tools")
        assert callable(registry.discover_tools)

    def test_registry_has_load_tool_method(self) -> None:
        """Test that ToolRegistry has load_tool method."""
        from cogito.orchestration.registry import ToolRegistry

        registry = ToolRegistry()
        assert hasattr(registry, "load_tool")
        assert callable(registry.load_tool)

    def test_registry_has_get_tool_method(self) -> None:
        """Test that ToolRegistry has get_tool method."""
        from cogito.orchestration.registry import ToolRegistry

        registry = ToolRegistry()
        assert hasattr(registry, "get_tool")
        assert callable(registry.get_tool)

    def test_registry_has_list_tools_method(self) -> None:
        """Test that ToolRegistry has list_tools method."""
        from cogito.orchestration.registry import ToolRegistry

        registry = ToolRegistry()
        assert hasattr(registry, "list_tools")
        assert callable(registry.list_tools)


class TestProcessingProtocolConformance:
    """Test that processing layer implementations conform to ProcessingProtocol."""

    def test_template_renderer_conforms_to_processing_protocol(self) -> None:
        """Test that TemplateRenderer conforms to ProcessingProtocol."""
        from cogito.processing.renderer import TemplateRenderer

        renderer = TemplateRenderer()
        assert isinstance(renderer, ProcessingProtocol)

    def test_parameter_validator_conforms_to_validation_protocol(self) -> None:
        """Test that ParameterValidator conforms to ValidationProtocol."""
        from cogito.processing.validator import ParameterValidator

        validator = ParameterValidator()
        assert isinstance(validator, ValidationProtocol)

    def test_schema_validator_conforms_to_schema_validation_protocol(self) -> None:
        """Test that SchemaValidator conforms to SchemaValidationProtocol."""
        from cogito.processing.validator import SchemaValidator

        validator = SchemaValidator()
        assert isinstance(validator, SchemaValidationProtocol)

    def test_renderer_has_render_method(self) -> None:
        """Test that TemplateRenderer has render method."""
        from cogito.processing.renderer import TemplateRenderer

        renderer = TemplateRenderer()
        assert hasattr(renderer, "render")
        assert callable(renderer.render)

    def test_renderer_has_validate_template_syntax_method(self) -> None:
        """Test that TemplateRenderer has validate_template_syntax method."""
        from cogito.processing.renderer import TemplateRenderer

        renderer = TemplateRenderer()
        assert hasattr(renderer, "validate_template_syntax")
        assert callable(renderer.validate_template_syntax)

    def test_parameter_validator_has_validate_parameters_method(self) -> None:
        """Test that ParameterValidator has validate_parameters method."""
        from cogito.processing.validator import ParameterValidator

        validator = ParameterValidator()
        assert hasattr(validator, "validate_parameters")
        assert callable(validator.validate_parameters)

    def test_schema_validator_has_validate_tool_spec_method(self) -> None:
        """Test that SchemaValidator has validate_tool_spec method."""
        from cogito.processing.validator import SchemaValidator

        validator = SchemaValidator()
        assert hasattr(validator, "validate_tool_spec")
        assert callable(validator.validate_tool_spec)


class TestStorageProtocolConformance:
    """Test that storage layer implementations conform to StorageProtocol."""

    def test_process_memory_store_conforms_to_storage_protocol(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Test that ProcessMemoryStore conforms to StorageProtocol."""
        from pathlib import Path

        from cogito.storage.process_memory import ProcessMemoryStore

        memory_file = Path(tmp_path) / "test_memory.jsonl"
        store = ProcessMemoryStore(memory_file)
        assert isinstance(store, StorageProtocol)

    def test_knowledge_graph_conforms_to_knowledge_graph_protocol(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Test that KnowledgeGraph conforms to KnowledgeGraphProtocol."""
        from pathlib import Path

        from cogito.storage.knowledge_graph import KnowledgeGraph
        from cogito.storage.process_memory import ProcessMemoryStore

        memory_file = Path(tmp_path) / "test_memory.jsonl"
        store = ProcessMemoryStore(memory_file)
        graph = KnowledgeGraph(store)
        assert isinstance(graph, KnowledgeGraphProtocol)

    def test_process_memory_has_append_entry_method(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Test that ProcessMemoryStore has append_entry method."""
        from pathlib import Path

        from cogito.storage.process_memory import ProcessMemoryStore

        memory_file = Path(tmp_path) / "test_memory.jsonl"
        store = ProcessMemoryStore(memory_file)
        assert hasattr(store, "append_entry")
        assert callable(store.append_entry)

    def test_process_memory_has_get_entry_method(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Test that ProcessMemoryStore has get_entry method."""
        from pathlib import Path

        from cogito.storage.process_memory import ProcessMemoryStore

        memory_file = Path(tmp_path) / "test_memory.jsonl"
        store = ProcessMemoryStore(memory_file)
        assert hasattr(store, "get_entry")
        assert callable(store.get_entry)

    def test_process_memory_has_search_entries_method(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Test that ProcessMemoryStore has search_entries method."""
        from pathlib import Path

        from cogito.storage.process_memory import ProcessMemoryStore

        memory_file = Path(tmp_path) / "test_memory.jsonl"
        store = ProcessMemoryStore(memory_file)
        assert hasattr(store, "search_entries")
        assert callable(store.search_entries)

    def test_knowledge_graph_has_build_graph_method(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Test that KnowledgeGraph has build_graph method."""
        from pathlib import Path

        from cogito.storage.knowledge_graph import KnowledgeGraph
        from cogito.storage.process_memory import ProcessMemoryStore

        memory_file = Path(tmp_path) / "test_memory.jsonl"
        store = ProcessMemoryStore(memory_file)
        graph = KnowledgeGraph(store)
        assert hasattr(graph, "build_graph")
        assert callable(graph.build_graph)

    def test_knowledge_graph_has_get_related_method(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Test that KnowledgeGraph has get_related method."""
        from pathlib import Path

        from cogito.storage.knowledge_graph import KnowledgeGraph
        from cogito.storage.process_memory import ProcessMemoryStore

        memory_file = Path(tmp_path) / "test_memory.jsonl"
        store = ProcessMemoryStore(memory_file)
        graph = KnowledgeGraph(store)
        assert hasattr(graph, "get_related")
        assert callable(graph.get_related)


class TestProtocolRuntimeChecking:
    """Test that @runtime_checkable decorator enables isinstance checks."""

    def test_orchestration_protocol_is_runtime_checkable(self) -> None:
        """Test that OrchestrationProtocol can be used with isinstance."""
        from cogito.orchestration.executor import ToolExecutor

        executor = ToolExecutor()
        # If not @runtime_checkable, this would raise TypeError
        result = isinstance(executor, OrchestrationProtocol)
        assert result is True

    def test_processing_protocol_is_runtime_checkable(self) -> None:
        """Test that ProcessingProtocol can be used with isinstance."""
        from cogito.processing.renderer import TemplateRenderer

        renderer = TemplateRenderer()
        result = isinstance(renderer, ProcessingProtocol)
        assert result is True

    def test_storage_protocol_is_runtime_checkable(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Test that StorageProtocol can be used with isinstance."""
        from pathlib import Path

        from cogito.storage.process_memory import ProcessMemoryStore

        memory_file = Path(tmp_path) / "test_memory.jsonl"
        store = ProcessMemoryStore(memory_file)
        result = isinstance(store, StorageProtocol)
        assert result is True


class TestProtocolImports:
    """Test that protocols can be imported from contracts module."""

    def test_import_orchestration_protocol(self) -> None:
        """Test importing OrchestrationProtocol."""
        from cogito.contracts import OrchestrationProtocol

        assert OrchestrationProtocol is not None

    def test_import_tool_registry_protocol(self) -> None:
        """Test importing ToolRegistryProtocol."""
        from cogito.contracts import ToolRegistryProtocol

        assert ToolRegistryProtocol is not None

    def test_import_processing_protocol(self) -> None:
        """Test importing ProcessingProtocol."""
        from cogito.contracts import ProcessingProtocol

        assert ProcessingProtocol is not None

    def test_import_validation_protocol(self) -> None:
        """Test importing ValidationProtocol."""
        from cogito.contracts import ValidationProtocol

        assert ValidationProtocol is not None

    def test_import_schema_validation_protocol(self) -> None:
        """Test importing SchemaValidationProtocol."""
        from cogito.contracts import SchemaValidationProtocol

        assert SchemaValidationProtocol is not None

    def test_import_storage_protocol(self) -> None:
        """Test importing StorageProtocol."""
        from cogito.contracts import StorageProtocol

        assert StorageProtocol is not None

    def test_import_knowledge_graph_protocol(self) -> None:
        """Test importing KnowledgeGraphProtocol."""
        from cogito.contracts import KnowledgeGraphProtocol

        assert KnowledgeGraphProtocol is not None

    def test_import_ui_protocol(self) -> None:
        """Test importing UIProtocol."""
        from cogito.contracts import UIProtocol

        assert UIProtocol is not None

    def test_import_integration_protocol(self) -> None:
        """Test importing IntegrationProtocol."""
        from cogito.contracts import IntegrationProtocol

        assert IntegrationProtocol is not None

    def test_all_exports_present(self) -> None:
        """Test that __all__ exports all protocols."""
        from cogito import contracts

        assert "OrchestrationProtocol" in contracts.__all__
        assert "ToolRegistryProtocol" in contracts.__all__
        assert "ProcessingProtocol" in contracts.__all__
        assert "ValidationProtocol" in contracts.__all__
        assert "SchemaValidationProtocol" in contracts.__all__
        assert "StorageProtocol" in contracts.__all__
        assert "KnowledgeGraphProtocol" in contracts.__all__
        assert "UIProtocol" in contracts.__all__
        assert "IntegrationProtocol" in contracts.__all__
