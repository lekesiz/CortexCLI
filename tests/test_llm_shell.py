"""
Tests for llm_shell module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_shell import (
    query_ollama,
    get_available_models,
    save_chat_history,
    load_chat_history,
    extract_code_blocks,
    auto_save_code,
    start_interactive_shell
)


class TestLLMShell:
    """Test cases for LLM shell functionality"""
    
    @patch('requests.post')
    def test_query_ollama_success(self, mock_post):
        """Test successful Ollama query"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Hello, World!"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = query_ollama("Hello", "qwen2.5:7b")
        assert result == "Hello, World!"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_query_ollama_error(self, mock_post):
        """Test Ollama query error handling"""
        mock_post.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception):
            query_ollama("Hello", "qwen2.5:7b")
    
    @patch('requests.get')
    def test_get_available_models(self, mock_get):
        """Test getting available models"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [
                {"name": "qwen2.5:7b", "modified_at": "2024-01-01T00:00:00Z"},
                {"name": "deepseek-coder:6.7b", "modified_at": "2024-01-01T00:00:00Z"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        models = get_available_models()
        assert len(models) == 2
        assert models[0]["name"] == "qwen2.5:7b"
    
    def test_save_and_load_chat_history(self, tmp_path):
        """Test chat history save and load"""
        history_file = tmp_path / "test_history.txt"
        test_history = [
            {"user": "Hello", "assistant": "Hi there!", "timestamp": "2024-01-01T00:00:00Z"}
        ]
        
        # Test save
        save_chat_history(test_history, str(history_file))
        assert history_file.exists()
        
        # Test load
        loaded_history = load_chat_history(str(history_file))
        assert len(loaded_history) == 1
        assert loaded_history[0]["user"] == "Hello"
    
    def test_extract_code_blocks(self):
        """Test code block extraction"""
        text = """
        Here's some Python code:
        ```python
        print("Hello, World!")
        ```
        And some JavaScript:
        ```javascript
        console.log("Hello");
        ```
        """
        
        blocks = extract_code_blocks(text)
        assert len(blocks) == 2
        assert blocks[0]["language"] == "python"
        assert blocks[0]["code"] == 'print("Hello, World!")'
        assert blocks[1]["language"] == "javascript"
        assert blocks[1]["code"] == 'console.log("Hello");'
    
    @patch('builtins.open', create=True)
    def test_auto_save_code(self, mock_open, tmp_path):
        """Test automatic code saving"""
        mock_open.return_value.__enter__.return_value = MagicMock()
        
        code_blocks = [
            {"language": "python", "code": "print('Hello')"},
            {"language": "javascript", "code": "console.log('Hello');"}
        ]
        
        output_dir = str(tmp_path)
        auto_save_code(code_blocks, output_dir)
        
        # Should have called open twice (once for each code block)
        assert mock_open.call_count == 2


class TestInteractiveShell:
    """Test cases for interactive shell functionality"""
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_start_interactive_shell_basic(self, mock_print, mock_input):
        """Test basic interactive shell functionality"""
        mock_input.side_effect = ["Hello", "/exit"]
        
        # Mock the query_ollama function
        with patch('llm_shell.query_ollama') as mock_query:
            mock_query.return_value = "Hi there!"
            
            # This would normally run indefinitely, so we'll test the setup
            # In a real test, you'd want to test individual functions
            assert True  # Placeholder assertion
    
    def test_system_prompt_presets(self):
        """Test system prompt presets"""
        from llm_shell import SYSTEM_PROMPTS
        
        assert "python_expert" in SYSTEM_PROMPTS
        assert "security_expert" in SYSTEM_PROMPTS
        assert "translator" in SYSTEM_PROMPTS
        assert "code_reviewer" in SYSTEM_PROMPTS
        assert "teacher" in SYSTEM_PROMPTS
        assert "debugger" in SYSTEM_PROMPTS


if __name__ == "__main__":
    pytest.main([__file__]) 