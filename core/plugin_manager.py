import importlib
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self, plugin_dir: str = "core/plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Any] = {}
        self.load_plugins()
        logger.info(f"Initialized PluginManager with plugins: {list(self.plugins.keys())}")

    def load_plugins(self):
        logger.info(f"Loading plugins from directory: {self.plugin_dir}")
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]  # Remove .py extension
                module_path = f"{self.plugin_dir.replace('/', '.')}.{plugin_name}"
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, 'register_plugin'):
                        plugin_info = module.register_plugin()
                        self.plugins[plugin_info['name']] = plugin_info
                        logger.info(f"Successfully loaded plugin: {plugin_info['name']}")
                    else:
                        logger.warning(f"Module {module_path} does not have a register_plugin function")
                except Exception as e:
                    logger.error(f"Error loading plugin {filename}: {str(e)}")

        logger.info(f"Loaded plugins: {list(self.plugins.keys())}")

    def get_plugin(self, name: str) -> Dict[str, Any]:
        plugin = self.plugins.get(name)
        if plugin:
            logger.info(f"Retrieved plugin: {name}")
        else:
            logger.warning(f"Plugin not found: {name}")
        return plugin

    def list_plugins(self) -> Dict[str, str]:
        return {name: plugin.get('description', 'No description available') 
                for name, plugin in self.plugins.items()}

    def execute_plugin(self, name: str, *args, **kwargs):
        plugin = self.get_plugin(name)
        if plugin and 'function' in plugin:
            try:
                return plugin['function'](*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing plugin {name}: {str(e)}")
                return None
        else:
            logger.error(f"Plugin {name} not found or has no executable function")
            return None