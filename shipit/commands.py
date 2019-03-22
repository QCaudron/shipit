"""
Creating and deploying shipit projects
"""
import logging
import tempfile
import shutil
import json
import docker
import os
import yaml


logger = logging.getLogger('shipit')


def load_config():
    with open("shipit.yml") as config_file:
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
    return config_data


def initialize():
    """
    Place a default shipit config in the local directory
    """
    shipit_path = os.path.dirname(os.path.realpath(__file__))
    shutil.copy(os.path.join(shipit_path, "shipit.yml"), "shipit.yml")
    logger.info("Created `shipit.yml`")


def build(tag="shipit"):
    logger.info("Building...")
    shipit_path = os.path.dirname(os.path.realpath(__file__))
    config = load_config()

    build_dir = tempfile.mkdtemp()

    # Copy models to /temp/models/ folder
    for name, model_settings in config.get("models").items():
        # Model files get copied to an identical path 
        # inside the image's `models` folder. 
        # So the local `models/sklearn_rfc.pkl` will get copied to
        # `/temp/models/sklearn_rfc.pkl`
        # or `really/long/path/model.pkl` -> `/temp/models/really/long/path/model.pkl`
        # This way we can reuse the path from the shipit.yml config
        # to load in the models and their associated metadata
        path = model_settings.get("path")
        destination = os.path.join(build_dir, path)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy(path, destination)
    
    # Create requirements file
    shutil.copy("requirements.txt", build_dir)

    # Copy over the config so we know stuff about the models
    shutil.copy("shipit.yml", build_dir)

    # Copy the web app over
    shutil.copy(os.path.join(shipit_path, "app.py"), build_dir)
    shutil.copytree(os.path.join(shipit_path, "config/"), os.path.join(build_dir, "config"))

    # Template the Dockerfile to temp/Dockerfile
    shutil.copy(os.path.join(shipit_path, "Dockerfile"), build_dir)

    # Build the image
    client = docker.from_env()
    # Use the low level build API to get the build stream and
    # print it
    stream = client.api.build(path=build_dir, tag=tag)
    for output in stream:
        lines = output.splitlines()
        for line in lines:
            line = json.loads(line)
            line = line.get("stream", "")
            line = line.rstrip()
            logger.info(line)
