"""
Creating and deploying shipit projects
"""
import logging
import tempfile
import inspect
import shutil
import json
import docker
import os
import delegator

from .utils import load_config, import_func


logger = logging.getLogger("shipit")


def get_var_string(vars):
    """
    Turn dictionary of variables into terraform argument string
    """
    args = []
    for key, val in vars.items():
        current = "-var='{}={}'".format(key, val)
        args.append(current)
    return ' '.join(args)


def initialize():
    """
    Place a default shipit config in the local directory
    """
    if os.path.exists("shipit.yml"):
        logger.info("Local `shipit.yml` already exists.")
        return
    shipit_path = os.path.dirname(os.path.realpath(__file__))
    shutil.copy(os.path.join(shipit_path, "shipit.yml"), "shipit.yml")
    logger.info("Created `shipit.yml`")


def build(tag="shipit", version=1, verbosity=1):
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

        model_path = model_settings.get("path")
        destination = os.path.join(build_dir, model_path)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy(model_path, destination)

        # Grab any related pre/post processing scripts
        for stage in ["preprocess", "postprocess"]:
            # TODO: Making a lot of assumptions here about the function
            # being at the top level of a python module file
            # Make this more robust
            dot_path = model_settings.get(stage)
            if dot_path is not None:
                file_path = "/".join(dot_path.split('.')[:-1])
                file_path = "{}.py".format(file_path)
                destination = os.path.join(build_dir, file_path)
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy(file_path, destination)

    requirements_path = config.get("meta", {}).get("requirements")
    
    if verbosity > 1:
        if not requirements_path:
            logger.info("No requirements file specified.")
        logger.info("Using requirements file: {}".format(requirements_path))

    # Create requirements file
    shutil.copy(requirements_path, build_dir)

    # Copy over the config so we know stuff about the models
    shutil.copy("shipit.yml", build_dir)


    # Write version to file
    version_file_path = os.path.join(build_dir, "VERSION")
    with open(version_file_path, "w") as version_file:
        version_file.write(str(version))

    # Copy the web app over
    shutil.copy(os.path.join(shipit_path, "utils.py"), build_dir)
    shutil.copy(os.path.join(shipit_path, "app.py"), build_dir)
    shutil.copytree(
        os.path.join(shipit_path, "config/"), os.path.join(build_dir, "config")
    )

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

            try:
                formatted = json.loads(line)
                if "stream" in formatted:
                    formatted = formatted.get("stream", "")
                    formatted = formatted.rstrip()
                if verbosity > 1:
                    logger.info(formatted)
            except:
                logger.warning(line)


def deploy(tag="shipit", verbosity=1):
    config = load_config()

    vars = {
        "project_name": config.get("meta", {}).get("project_name", "shipit"),
        "aws_profile": config.get("meta", {}).get("aws_profile", "default"),
        "region": config.get("meta", {}).get("aws_region", "us-west-2"),
    }

    current_dir = os.getcwd()
    state_path = os.path.join(current_dir, "terraform.tfstate")
    shipit_path = os.path.dirname(os.path.realpath(__file__))
    plan_path = os.path.join(shipit_path, "terraform")

    cmd = delegator.run("terraform output -state={} ecr_repository".format(state_path))
    repository = cmd.out.strip()
    cmd = delegator.run("terraform output -state={} project_version".format(state_path))
    current_version = cmd.out.strip()

    try:
        current_version = int(current_version)
    except ValueError:
        current_version = 0

    new_version = current_version + 1

    vars["project_version"] = new_version

    logger.info("Building and Deploying {}".format(vars["project_name"]))
    logger.info("Provider: {}".format(config.get("meta", {}).get("provider")))
    logger.info("AWS Profile: {}".format(vars["aws_profile"]))
    logger.info("AWS Region: {}".format(vars["region"]))

    logger.info("Initializing Terraform Installation")
    delegator.run("terraform init -input=false -from-module={}".format(
        plan_path
    ))

    if not repository:
        logger.info("No existing repository, creating infrastructure.")
        # TODO: Selectively create just the ECR Repository to push image to
        # This will prevent spinning up a service which can't run yet
        apply_cmd = "terraform apply {vars} -state={state_path} -input=false -auto-approve {plan_path}".format(
            state_path=state_path,
            plan_path=plan_path,
            vars=get_var_string(vars)
        )
        output = delegator.run(apply_cmd)
        cmd = delegator.run("terraform output -state={} ecr_repository".format(state_path))
        repository = cmd.out.strip()

    logger.info("Building Docker image version {}".format(vars["project_version"]))
    tag = "{}:{}".format(repository, vars["project_version"])
    build(tag=tag, version=vars["project_version"], verbosity=verbosity)

    logger.info("Pushing docker image...")
    delegator.run("$(aws --profile={} ecr get-login --no-include-email --region us-west-2)".format(vars["aws_profile"]))
    push_cmd = delegator.run("docker push {}".format(tag))
    if verbosity > 1:
        logger.info(push_cmd.out)

    logger.info("Updating Services")
    delegator.run("terraform apply {vars} -state={state_path} -input=false -auto-approve {plan_path}".format(
        state_path=state_path,
        plan_path=plan_path,
        vars=get_var_string(vars)
    ))
    cmd = delegator.run("terraform output -state={} project_version".format(state_path))
    project_version = cmd.out.strip()
    cmd = delegator.run("terraform output -state={} alb_dns_name".format(state_path))
    endpoint = cmd.out.strip()
    logger.info("{:20}: {}".format("Project", vars["project_name"]))
    logger.info("{:20}: {}".format("Endpoint", endpoint))
    logger.info("{:20}: {}".format("Version", project_version))


def destroy(tag="shipit"):
    config = load_config()

    vars = {
        "project_name": config.get("meta", {}).get("project_name", "shipit"),
        "aws_profile": config.get("meta", {}).get("aws_profile", "default"),
        "region": config.get("meta", {}).get("aws_region", "us-west-2"),
    }

    current_dir = os.getcwd()
    state_path = os.path.join(current_dir, "terraform.tfstate")
    shipit_path = os.path.dirname(os.path.realpath(__file__))
    plan_path = os.path.join(shipit_path, "terraform")

    cmd = delegator.run("terraform output -state={} project_version".format(state_path))
    current_version = cmd.out.strip()
    try:
        current_version = int(current_version)
    except TypeError:
        current_version = 0
    
    vars["project_version"] = current_version

    logger.info("Destroying Project {}".format(vars["project_name"]))
    cmd = delegator.run("terraform destroy {vars} -state={state_path} -input=false -auto-approve {plan_path}".format(
        state_path=state_path,
        plan_path=plan_path,
        vars=get_var_string(vars)
    ))
    if cmd.ok:
        logger.info("Complete")
    else:
        logger.info("There was an error: ")
        logger.info(cmd.out)
