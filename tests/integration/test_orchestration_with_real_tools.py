"""Integration tests for orchestration layer with real thinking tools.

Tests ToolRegistry and ToolExecutor with all 9 production thinking tools.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml

from cogito.orchestration.executor import ToolExecutionError, ToolExecutor
from cogito.orchestration.registry import ToolRegistry

# Get path to examples directory
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


class TestToolRegistryWithRealTools:
    """Test ToolRegistry with production thinking tools."""

    def test_discover_all_example_tools(self) -> None:
        """Test that registry discovers all 9 example tools."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        count = registry.discover_tools()

        # Should find 9 tools
        assert count == 9

        # Verify specific tools are found
        tools = registry.list_tools()
        assert "think_aloud" in tools
        assert "assumption_check" in tools
        assert "fresh_eyes_exercise" in tools
        assert "code_review_checklist" in tools
        assert "architecture_review" in tools
        assert "session_handover" in tools
        assert "context_preservation" in tools
        assert "error_analysis" in tools
        assert "five_whys" in tools

    def test_category_organization_with_real_tools(self) -> None:
        """Test that tools are properly categorized."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        categories = registry.list_categories()

        # Should have 4 categories
        assert "metacognition" in categories
        assert "review" in categories
        assert "handoff" in categories
        assert "debugging" in categories

        # Verify category membership
        meta_tools = registry.get_tools_by_category("metacognition")
        assert len(meta_tools) == 3
        assert "think_aloud" in meta_tools
        assert "assumption_check" in meta_tools
        assert "fresh_eyes_exercise" in meta_tools

        review_tools = registry.get_tools_by_category("review")
        assert len(review_tools) == 2
        assert "code_review_checklist" in review_tools
        assert "architecture_review" in review_tools

        handoff_tools = registry.get_tools_by_category("handoff")
        assert len(handoff_tools) == 2
        assert "session_handover" in handoff_tools
        assert "context_preservation" in handoff_tools

        debug_tools = registry.get_tools_by_category("debugging")
        assert len(debug_tools) == 2
        assert "error_analysis" in debug_tools
        assert "five_whys" in debug_tools

    def test_get_tool_specs(self) -> None:
        """Test retrieving tool specifications from registry."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        # Get a specific tool
        think_aloud = registry.get_tool("think_aloud")
        assert think_aloud is not None
        assert think_aloud["metadata"]["name"] == "think_aloud"
        assert think_aloud["metadata"]["display_name"] == "Think Aloud Protocol"
        assert "template" in think_aloud
        assert "parameters" in think_aloud

    def test_hot_reload_real_tool(self, tmp_path: Path) -> None:
        """Test hot-reloading a real tool after modification."""
        # Copy think_aloud to temp directory
        original_file = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"
        with open(original_file, "r", encoding="utf-8") as f:
            original_spec = yaml.safe_load(f)

        temp_file = tmp_path / "think_aloud.yml"
        with open(temp_file, "w", encoding="utf-8") as f:
            yaml.dump(original_spec, f)

        # Load into registry
        registry = ToolRegistry(tool_dirs=[tmp_path])
        registry.discover_tools()

        # Modify the tool
        modified_spec = original_spec.copy()
        modified_spec["metadata"] = modified_spec["metadata"].copy()
        modified_spec["metadata"]["version"] = "999.0.0"

        with open(temp_file, "w", encoding="utf-8") as f:
            yaml.dump(modified_spec, f)

        # Hot-reload
        reloaded = registry.reload_tool("think_aloud")

        assert reloaded["metadata"]["version"] == "999.0.0"
        assert registry.get_tool("think_aloud")["metadata"]["version"] == "999.0.0"


class TestToolExecutorWithRealTools:
    """Test ToolExecutor with production thinking tools."""

    def test_execute_think_aloud_with_defaults(self) -> None:
        """Test executing think_aloud with default parameters."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name("think_aloud", registry)

        # Should contain expected sections
        assert "Think Aloud Protocol" in result
        assert "Standard Think Aloud" in result

    def test_execute_think_aloud_with_custom_params(self) -> None:
        """Test executing think_aloud with custom parameters."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name(
            "think_aloud",
            registry,
            {"depth": "detailed", "focus": "Performance optimization"},
        )

        assert "Think Aloud Protocol" in result
        assert "Detailed Think Aloud" in result
        assert "Performance optimization" in result

    def test_execute_assumption_check(self) -> None:
        """Test executing assumption_check tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name("assumption_check", registry)

        assert "Assumption Check" in result

    def test_execute_fresh_eyes_exercise(self) -> None:
        """Test executing fresh_eyes_exercise tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name("fresh_eyes_exercise", registry)

        assert "Fresh Eyes Exercise" in result

    def test_execute_code_review_checklist(self) -> None:
        """Test executing code_review_checklist tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name("code_review_checklist", registry)

        assert "Code Review Checklist" in result
        assert "Five Cornerstones" in result

    def test_execute_architecture_review(self) -> None:
        """Test executing architecture_review tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name("architecture_review", registry)

        assert "Architecture Review" in result

    def test_execute_session_handover(self) -> None:
        """Test executing session_handover tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name("session_handover", registry)

        assert "Session Handover" in result

    def test_execute_context_preservation(self) -> None:
        """Test executing context_preservation tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name("context_preservation", registry)

        assert "Context Preservation" in result

    def test_execute_error_analysis(self) -> None:
        """Test executing error_analysis tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name(
            "error_analysis",
            registry,
            {
                "error_type": "runtime",
                "error_description": "NullPointerException in UserService",
            },
        )

        assert "Error Analysis" in result
        assert "NullPointerException" in result

    def test_execute_five_whys(self) -> None:
        """Test executing five_whys tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()
        result = executor.execute_by_name(
            "five_whys",
            registry,
            {"problem": "Users are experiencing slow page load times"},
        )

        assert "Five Whys Analysis" in result
        assert "slow page load times" in result

    def test_execute_all_tools_successfully(self) -> None:
        """Test that all 9 tools can be executed without errors."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()

        # List of all tools with minimal required parameters
        tools_to_test = [
            ("think_aloud", {}),
            ("assumption_check", {}),
            ("fresh_eyes_exercise", {}),
            ("code_review_checklist", {}),
            ("architecture_review", {}),
            ("session_handover", {}),
            ("context_preservation", {}),
            ("error_analysis", {"error_type": "runtime", "error_description": "Test"}),
            ("five_whys", {"problem": "Test problem"}),
        ]

        for tool_name, params in tools_to_test:
            result = executor.execute_by_name(tool_name, registry, params)
            assert isinstance(result, str)
            assert len(result) > 0


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_full_workflow_discovery_to_execution(self) -> None:
        """Test full workflow from discovery to execution."""
        # Step 1: Create registry and discover tools
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        discovered_count = registry.discover_tools()

        assert discovered_count == 9

        # Step 2: Verify tools are discoverable
        tools = registry.list_tools()
        assert "think_aloud" in tools

        # Step 3: Get tool spec
        tool_spec = registry.get_tool("think_aloud")
        assert tool_spec is not None

        # Step 4: Execute via registry lookup
        executor = ToolExecutor()
        result_by_name = executor.execute_by_name("think_aloud", registry)
        assert "Think Aloud Protocol" in result_by_name

        # Step 5: Execute via direct spec
        result_direct = executor.execute(tool_spec)
        assert "Think Aloud Protocol" in result_direct

        # Both methods should produce same result
        assert result_by_name == result_direct

    def test_category_based_execution(self) -> None:
        """Test discovering and executing all tools in a category."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()

        # Get all metacognition tools
        meta_tools = registry.get_tools_by_category("metacognition")
        assert len(meta_tools) == 3

        # Execute each one
        for tool_name in meta_tools:
            result = executor.execute_by_name(tool_name, registry)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_error_handling_invalid_tool(self) -> None:
        """Test error handling for nonexistent tool."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()

        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute_by_name("nonexistent_tool", registry)

        assert "not found in registry" in str(exc_info.value).lower()
        assert exc_info.value.phase == "lookup"

    def test_parameter_validation_integration(self) -> None:
        """Test that parameter validation works in full pipeline."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()

        # Test with invalid parameter type
        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute_by_name(
                "think_aloud", registry, {"depth": 123}  # Should be string
            )

        assert exc_info.value.phase == "validation"

    def test_template_rendering_integration(self) -> None:
        """Test that template rendering works with validated parameters."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()

        # Execute with parameters that should appear in output
        result = executor.execute_by_name(
            "error_analysis",
            registry,
            {
                "error_type": "logic",
                "error_description": "Test error description here",
            },
        )

        # Verify both parameter and template content appear
        assert "Test error description here" in result
        assert "Error Analysis" in result


class TestPerformanceWithRealTools:
    """Test performance characteristics with real tools."""

    def test_caching_improves_access_speed(self) -> None:
        """Test that tool caching works correctly."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        # First access loads from cache
        tool1 = registry.get_tool("think_aloud")
        # Second access should return same cached object
        tool2 = registry.get_tool("think_aloud")

        # Should be the same object (cached)
        assert tool1 is tool2

    def test_multiple_executions_same_tool(self) -> None:
        """Test executing the same tool multiple times."""
        registry = ToolRegistry(tool_dirs=[EXAMPLES_DIR])
        registry.discover_tools()

        executor = ToolExecutor()

        # Execute same tool with different parameters
        result1 = executor.execute_by_name(
            "think_aloud", registry, {"depth": "quick"}
        )
        result2 = executor.execute_by_name(
            "think_aloud", registry, {"depth": "standard"}
        )
        result3 = executor.execute_by_name(
            "think_aloud", registry, {"depth": "detailed"}
        )

        # All should succeed and produce different outputs
        assert "quick" in result1.lower()
        assert "standard" in result2.lower()
        assert "detailed" in result3.lower()
