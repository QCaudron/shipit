# ShipIt

Easily deploy your machine learning models to an API in the cloud.

## Quickstart

1. Install and configure awscli
1. Install terraform
1. `pip install shipit`
1. `shipit init`
1. Edit the newly created `shipit.yml` See [configuration](#configuration)
1. `shipit deploy`

You will get an output that tells you the version and what the endpoint is.

```
Project             : demo
Endpoint            : production-alb-demo-553835794.us-west-2.elb.amazonaws.com
Version             : 2
```

## How it Works
Shipit wraps tools like docker, awscli, and terraform to make it easy to deploy production ready web APIs for your machine learning models. First a docker image is built based on the configurat


## Running Locally

You can spin up your container locally like this:

```
shipit build -t yourtagname
docker run -p 5000:80 -it yourtagname
```

You now have your models being served from a web API. Visit `localhost:5000/` to see the list of available models.

## Commands

shipit deploy -t [yourtag] --verbosity 1
: Build and deploy the shipit project. All arguments are optional.

shipit destroy
: Use terraform to destroy 

shipit build -t [yourtag] --verbosity 1
: Build the docker image and tag it. All arguments are optional.

## Usage

Getting predictions requires sending a `POST` to the relevant model's predict endpoint:

```
http://[your-endpoint]/predict/[model-name]
```

The payload should be a JSON serialized array or 2d array (for multiple predictions) to the provided model's endpoint. For example, a model that takes three features would look like this:

```
[33, 4, 10]
```

In the case of doing multiple predictions, pass that in as a 2d array.

```
[
    [33, 4, 10],
    [32, 1, 5]
]
```

Here's an example using cURL.

```
curl -d '[[5, 1, 6], [1, 2, 3]]' -H "Content-Type: application/json" -X POST http://[your-endpoint]:5000/predict/[modelname]
```

The response will always be a 2d array, so if you send one data point expect a list back with only one row.

## Configuration <a name="configuration"></a>

The config file `shipit.yml` for your project is broken down into two major sections. 

### meta

project_name
:  A unique project name, used to namespace the resources created for your project.

requirements
:  Path to a requirements.txt file to install dependencies for your models

provider
:  For now this is always assumed to be `aws`

aws_profile
:  Name of the profile from your awscli credentials. 

aws_region
:  Which aws region to launch your service in.

### models

This section can contain one or more models you want to include in this API service. See `example/shipit.yml` as a reference.

path
:  The relative path of the pickled model file e.g. `models/my_model.pkl`

variety
:  One of `["sklearn", "keras"]`. Eventually we will add more model types.

preprocess
:  (optional) A python import dot path to a preprocess function. This function can perform manipulations of the API input before sending it to your model.

postprocess
:  (optional) A python import dot path to a postprocess function. This function can perform manipulations of the model's prediction output before returning it to the user.


## Formatting model data

First, ensure your features is a `(n_samples, n_features)`-shaped numpy array ( in standard `sklearn` form ). Turn this into a list ( so that we can JSON-serialise it ). 

## Saving models

Models from `scikit-learn` should be saved with `joblib`. Models from `keras` should be saved with `model.save()`. See `example/save_model_example.py`.

## To Do
- Deploy to Private VPN
- Route53 / private / public DNS
- Build an "export" feature for customization of Docker / terraform setup.
- Support XGBoost models
- Figure out why sklearn.linear_model.LinearRegression can't be pickled