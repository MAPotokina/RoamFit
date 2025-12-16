"""Tests for orchestrator workflow."""
from unittest.mock import MagicMock, Mock, patch

import pytest

from agents.strands_orchestrator import create_roamfit_orchestrator


class TestOrchestrator:
    """Tests for orchestrator workflow."""

    @patch("agents.strands_orchestrator.Agent")
    def test_orchestrator_creation(self, mock_agent_class):
        """Test orchestrator creation."""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        orchestrator = create_roamfit_orchestrator()

        assert orchestrator is not None
        mock_agent_class.assert_called_once()

    @patch("agents.strands_orchestrator.Agent")
    def test_orchestrator_call(self, mock_agent_class):
        """Test orchestrator call with query."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent.return_value = "Test response"
        mock_agent_class.return_value = mock_agent

        orchestrator = create_roamfit_orchestrator()
        response = orchestrator("test query")

        assert response == "Test response"
        mock_agent.assert_called_once_with("test query")

    @patch("agents.strands_orchestrator.Agent")
    def test_orchestrator_has_tools(self, mock_agent_class):
        """Test that orchestrator has all required tools."""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        create_roamfit_orchestrator()

        # Verify Agent was called with tools
        call_args = mock_agent_class.call_args
        assert "tools" in call_args.kwargs
        tools = call_args.kwargs["tools"]

        # Check that all expected agents are in tools (6 agents)
        assert len(tools) == 6

        # Check that all expected agents are in tools
        tool_names = [tool.__name__ for tool in tools]
        assert "equipment_detection_agent" in tool_names
        assert "workout_summary_agent" in tool_names
        assert "workout_generator_agent" in tool_names
        assert "graph_trends_agent" in tool_names
        assert "location_activity_agent" in tool_names
        assert "workout_management_agent" in tool_names

    @patch("agents.strands_orchestrator.Agent")
    def test_orchestrator_error_handling(self, mock_agent_class):
        """Test orchestrator error handling."""
        # Setup mock agent to raise exception
        mock_agent = MagicMock()
        mock_agent.side_effect = Exception("Orchestrator error")
        mock_agent_class.return_value = mock_agent

        orchestrator = create_roamfit_orchestrator()

        with pytest.raises(Exception, match="Orchestrator error"):
            orchestrator("test query")
