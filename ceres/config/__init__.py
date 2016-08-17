# coding: utf-8
import os

__all__ = ['AppConfig']

# for app config
app_config_module_path = os.environ.get('CERES_APP_CONFIG', '')
if not app_config_module_path:
    raise Exception('No CERES_APP_CONFIG in os environ')
app_config_module = __import__(app_config_module_path, fromlist=['Config'])

AppConfig = app_config_module.Config
