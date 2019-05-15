import yaml
import importlib


def load_config():
    with open("shipit.yml") as config_file:
        config_data = yaml.load(config_file)
    return config_data


def validate_config(config):
    """
    Validate the properties of a configuration file
    """
    project_name = config.get("meta", {}).get("project_name", "shipit"),
    if "_" in project_name:
        raise Exception("Project name cannot include '_'")


def import_func(dot_path):
    """
    Returns a class object from dot path notation
    """
    module_path, func_name = dot_path.rsplit('.', 1)
    imported_module = importlib.import_module(module_path)
    func = getattr(imported_module, func_name)
    return func