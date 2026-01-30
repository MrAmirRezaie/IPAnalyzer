"""Plugin manager for discovering and loading simple plugins."""
import os
import json
import importlib.util
from typing import Dict


class PluginManager:
    def __init__(self, plugin_dir: str = None):
        self.plugin_dir = plugin_dir or os.path.join(os.getcwd(), 'plugins')
        self.plugins: Dict[str, Dict] = {}
        self.load_plugins()

    def load_plugins(self):
        self.plugins = {}
        if not os.path.isdir(self.plugin_dir):
            return
        for name in os.listdir(self.plugin_dir):
            path = os.path.join(self.plugin_dir, name)
            if not os.path.isdir(path):
                continue
            config_path = os.path.join(path, 'plugin.json')
            if not os.path.exists(config_path):
                continue
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                main = cfg.get('main')
                main_path = os.path.join(path, main)
                if os.path.exists(main_path):
                    spec = importlib.util.spec_from_file_location(cfg.get('name', name), main_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.plugins[cfg.get('name', name)] = {'meta': cfg, 'module': module}
            except Exception:
                continue

    def list_plugins(self):
        return list(self.plugins.keys())

    def execute_plugin(self, plugin_name: str, *args, **kwargs):
        p = self.plugins.get(plugin_name)
        if not p:
            raise KeyError(f'Plugin not found: {plugin_name}')
        module = p['module']
        if hasattr(module, 'run'):
            return module.run(*args, **kwargs)
        raise AttributeError('Plugin module has no runnable entry point (run)')
