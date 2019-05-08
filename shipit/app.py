from flask import Flask, request, Response
import json
import yaml
import os
import numpy as np
from utils import import_func


class ShipIt:
    def __init__(self):
        """
        Load all sklearn and keras models into RAM.
        """
        with open("shipit.yml") as config_file:

            self.config = yaml.load(config_file)
        
        self.version = "0"
        if os.path.exists("./VERSION"):
            with open("VERSION")  as version_file:
                self.version = version_file.read().strip()

        # Load all models
        self.models = self.config.get("models", {})
        for model_name, model_settings in self.models.items():
            variety = model_settings.get("variety")
            if variety == "keras":
                # Dynamically import libraries only if needed
                from keras.models import load_model

                model_settings["instance"] = load_model(model_settings["path"])
            elif variety == "sklearn":
                from sklearn.externals import joblib

                model_settings["instance"] = joblib.load(model_settings["path"])
            else:
                raise Exception("Could not load model {}".format(model_name))
            
            # Get pre/post process functions
            for stage in ['preprocess', 'postprocess']:
                stage_dot = model_settings.get(stage, None)
                if stage_dot is not None:
                    func = import_func(stage_dot)
                    model_settings[stage] = func


    def index(self):
        model_index = {}
        for name, settings in self.models.items():
            model_index[name] = {
                "variety": settings["variety"]
            }
        return model_index


    def predict(self, model_name, request_data):
        """
        Given a model name and the JSON bundle from the API request,
        make predictions and return them in JSON form.
        """

        # Grab the correct model object
        model_settings = self.models.get(model_name, {})
        model = model_settings.get("instance", None)
        if model is None:
            raise ValueError("The specified model was not found.")

        # Parse prediction request data
        incoming = self._parse_request(request_data)

        # Optional preprocess step
        preprocess = model_settings.get('preprocess')
        if preprocess:
            incoming = preprocess(incoming)

        # Generate a prediction
        prediction = model.predict(incoming)
        prediction = np.atleast_2d(prediction).reshape(len(incoming), -1)
        prediction = prediction.tolist()

        postprocess = model_settings.get('postprocess')
        if postprocess:
            prediction = postprocess(prediction)
        return prediction

    def _parse_request(self, request_data):
        """
        Parse the JSON request and return it in numpy form. Validation occurs here.
        """
        if not isinstance(request_data, list):
            raise Exception("Your data is not shaped as an array.")

        # Single rows always get converted to 2d arrays
        data = np.atleast_2d(request_data)

        return data


# Instantiate ShipIt object
shipit = ShipIt()

# Spin up Flask app
app = Flask(__name__)


# Are we live ?
@app.route("/")
def index():
    model_index = shipit.index()
    resp = { "meta": { "version": shipit.version }, "models": model_index }
    return Response(json.dumps(resp), mimetype="application/json")


# Prediction endpoint
@app.route("/predict/<model_name>", methods=["POST"])
def predict(model_name):

    # Generate a prediction
    try:
        json_data = request.get_json()
        prediction = shipit.predict(model_name, json_data)
        return Response(json.dumps(prediction), mimetype="application/json")
    except Exception as e:
        data = {
            "error": str(e)
        }
        return Response(json.dumps(data), status=500, mimetype="application/json")


if __name__ == "__main__":
    app.run()
