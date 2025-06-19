"""
Tests for plugin system
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugin_system import PluginManager, BasePlugin


class MockPlugin(BasePlugin):
    """Mock plugin for testing"""
    
    def __init__(self):
        super().__init__()
        self.name = "mock_plugin"
        self.description = "A mock plugin for testing"
        self.version = "1.0.0"
    
    def execute(self, command, args):
        if command == "hello":
            return f"Hello {args[0]}!"
        elif command == "add":
            return sum(int(x) for x in args)
        else:
            return "Unknown command"


class TestPluginManager:
    """Test cases for PluginManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.plugin_manager = PluginManager()
        self.mock_plugin = MockPlugin()
    
    def test_plugin_manager_initialization(self):
        """Test PluginManager initialization"""
        assert self.plugin_manager.plugins == {}
        assert self.plugin_manager.plugins_dir == "plugins"
    
    def test_register_plugin(self):
        """Test plugin registration"""
        self.plugin_manager.register_plugin(self.mock_plugin)
        
        assert "mock_plugin" in self.plugin_manager.plugins
        assert self.plugin_manager.plugins["mock_plugin"] == self.mock_plugin
    
    def test_unregister_plugin(self):
        """Test plugin unregistration"""
        self.plugin_manager.register_plugin(self.mock_plugin)
        self.plugin_manager.unregister_plugin("mock_plugin")
        
        assert "mock_plugin" not in self.plugin_manager.plugins
    
    def test_execute_plugin_command(self):
        """Test plugin command execution"""
        self.plugin_manager.register_plugin(self.mock_plugin)
        
        result = self.plugin_manager.execute_plugin_command("mock_plugin", "hello", ["World"])
        assert result == "Hello World!"
        
        result = self.plugin_manager.execute_plugin_command("mock_plugin", "add", ["1", "2", "3"])
        assert result == 6
    
    def test_execute_plugin_command_not_found(self):
        """Test plugin command execution with non-existent plugin"""
        result = self.plugin_manager.execute_plugin_command("nonexistent", "hello", [])
        assert "Plugin 'nonexistent' not found" in result
    
    def test_list_plugins(self):
        """Test plugin listing"""
        self.plugin_manager.register_plugin(self.mock_plugin)
        
        plugins = self.plugin_manager.list_plugins()
        assert "mock_plugin" in plugins
        assert plugins["mock_plugin"]["name"] == "mock_plugin"
        assert plugins["mock_plugin"]["description"] == "A mock plugin for testing"
        assert plugins["mock_plugin"]["version"] == "1.0.0"
        assert plugins["mock_plugin"]["loaded"] is True
    
    @patch('os.path.exists')
    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    def test_load_plugin_from_file(self, mock_module_from_spec, mock_spec_from_file_location, mock_exists):
        """Test loading plugin from file"""
        mock_exists.return_value = True
        
        # Mock the plugin module
        mock_module = Mock()
        mock_plugin_instance = MockPlugin()
        mock_module.Plugin = Mock(return_value=mock_plugin_instance)
        mock_module_from_spec.return_value = mock_module
        
        # Mock the spec
        mock_spec = Mock()
        mock_spec_from_file_location.return_value = mock_spec
        
        # Test loading
        result = self.plugin_manager.load_plugin_from_file("test_plugin.py")
        assert result is True
        assert "test_plugin" in self.plugin_manager.plugins
    
    @patch('os.path.exists')
    def test_load_plugin_from_file_not_found(self, mock_exists):
        """Test loading non-existent plugin file"""
        mock_exists.return_value = False
        
        result = self.plugin_manager.load_plugin_from_file("nonexistent.py")
        assert result is False
    
    @patch('os.listdir')
    @patch.object(PluginManager, 'load_plugin_from_file')
    def test_discover_plugins(self, mock_load_plugin, mock_listdir):
        """Test plugin discovery"""
        mock_listdir.return_value = ["plugin1.py", "plugin2.py", "not_a_plugin.txt"]
        mock_load_plugin.return_value = True
        
        self.plugin_manager.discover_plugins()
        
        # Should have called load_plugin_from_file twice (for .py files only)
        assert mock_load_plugin.call_count == 2
        mock_load_plugin.assert_any_call("plugin1.py")
        mock_load_plugin.assert_any_call("plugin2.py")


class TestBasePlugin:
    """Test cases for BasePlugin"""
    
    def test_base_plugin_initialization(self):
        """Test BasePlugin initialization"""
        plugin = BasePlugin()
        
        assert plugin.name == "base_plugin"
        assert plugin.description == "Base plugin class"
        assert plugin.version == "1.0.0"
    
    def test_base_plugin_execute(self):
        """Test BasePlugin execute method"""
        plugin = BasePlugin()
        
        result = plugin.execute("test", [])
        assert result == "Command 'test' not implemented in base_plugin"
    
    def test_base_plugin_get_info(self):
        """Test BasePlugin get_info method"""
        plugin = BasePlugin()
        
        info = plugin.get_info()
        assert info["name"] == "base_plugin"
        assert info["description"] == "Base plugin class"
        assert info["version"] == "1.0.0"


class TestMockPlugin:
    """Test cases for MockPlugin"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.plugin = MockPlugin()
    
    def test_mock_plugin_initialization(self):
        """Test MockPlugin initialization"""
        assert self.plugin.name == "mock_plugin"
        assert self.plugin.description == "A mock plugin for testing"
        assert self.plugin.version == "1.0.0"
    
    def test_mock_plugin_hello_command(self):
        """Test MockPlugin hello command"""
        result = self.plugin.execute("hello", ["World"])
        assert result == "Hello World!"
    
    def test_mock_plugin_add_command(self):
        """Test MockPlugin add command"""
        result = self.plugin.execute("add", ["1", "2", "3"])
        assert result == 6
    
    def test_mock_plugin_unknown_command(self):
        """Test MockPlugin unknown command"""
        result = self.plugin.execute("unknown", [])
        assert result == "Unknown command"


if __name__ == "__main__":
    pytest.main([__file__]) 