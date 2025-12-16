"""Tests for LLM utility functions."""
from unittest.mock import MagicMock, Mock, patch

import pytest

from utils.llm import call_llm, call_vision


class TestCallLLM:
    """Tests for call_llm function."""

    @patch("utils.llm.OpenAI")
    @patch("utils.llm.save_llm_log")
    @patch("utils.llm.get_config")
    def test_call_llm_success(self, mock_get_config, mock_save_log, mock_openai_class):
        """Test successful LLM call."""
        # Setup config mock
        mock_get_config.return_value = {"OPENAI_API_KEY": "test-key"}

        # Setup OpenAI mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20

        mock_client.chat.completions.create.return_value = mock_response

        # Test
        result = call_llm("test prompt", agent_name="test_agent")

        # Assertions
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()
        mock_save_log.assert_called_once()

    @patch("utils.llm.OpenAI")
    @patch("utils.llm.save_llm_log")
    @patch("utils.llm.get_config")
    def test_call_llm_error(self, mock_get_config, mock_save_log, mock_openai_class):
        """Test LLM call with error."""
        # Setup config mock
        mock_get_config.return_value = {"OPENAI_API_KEY": "test-key"}

        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Test
        with pytest.raises(Exception):
            call_llm("test prompt", agent_name="test_agent")

        # Verify error was logged
        assert mock_save_log.called

    @patch("utils.llm.get_config")
    def test_call_llm_no_api_key(self, mock_get_config):
        """Test LLM call without API key."""
        mock_get_config.return_value = {"OPENAI_API_KEY": ""}
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            call_llm("test prompt")


class TestCallVision:
    """Tests for call_vision function."""

    @patch("builtins.open", create=True)
    @patch("utils.llm.OpenAI")
    @patch("utils.llm.save_llm_log")
    @patch("utils.llm.get_config")
    def test_call_vision_success(
        self, mock_get_config, mock_save_log, mock_openai_class, mock_open
    ):
        """Test successful vision API call."""
        # Setup config mock
        mock_get_config.return_value = {"OPENAI_API_KEY": "test-key"}

        # Setup OpenAI mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Detected: dumbbells, bench"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 10

        mock_client.chat.completions.create.return_value = mock_response

        # Mock file read
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake image data"
        mock_open.return_value.__enter__.return_value = mock_file

        # Test
        result = call_vision("test_image.jpg", "detect equipment", agent_name="test_agent")

        # Assertions
        assert "dumbbells" in result.lower() or "bench" in result.lower()
        mock_client.chat.completions.create.assert_called_once()
        mock_save_log.assert_called_once()

    @patch("builtins.open", create=True)
    @patch("utils.llm.OpenAI")
    @patch("utils.llm.save_llm_log")
    @patch("utils.llm.get_config")
    def test_call_vision_error(self, mock_get_config, mock_save_log, mock_openai_class, mock_open):
        """Test vision call with error."""
        # Setup config mock
        mock_get_config.return_value = {"OPENAI_API_KEY": "test-key"}

        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Vision API Error")

        # Mock file read
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake image data"
        mock_open.return_value.__enter__.return_value = mock_file

        # Test
        with pytest.raises(Exception):
            call_vision("test_image.jpg", "detect equipment", agent_name="test_agent")

        # Verify error was logged
        assert mock_save_log.called

    @patch("utils.llm.get_config")
    def test_call_vision_no_api_key(self, mock_get_config):
        """Test vision call without API key."""
        mock_get_config.return_value = {"OPENAI_API_KEY": ""}
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            call_vision("test_image.jpg", "detect equipment")
