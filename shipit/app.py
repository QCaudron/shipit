from flask import Flask, request, Response
import json
import yaml
import numpy as np


class ShipIt:
    def __init__(self):
        """
        Load all sklearn and keras models into RAM.
        """
        with open("shipit.yml") as config_file:
            self.config = yaml.load(config_file, Loader=yaml.FullLoader)

        # Load all models
        self.models = self.config.get("models", {})
        for name, settings in self.models.items():
            variety = settings.get("variety")
            if variety == "keras":
                # Dynamically import libraries only if needed
                from keras.models import load_model

                settings["instance"] = load_model(settings["path"])
            elif variety == "sklearn":
                from sklearn.externals import joblib

                settings["instance"] = joblib.load(settings["path"])
            else:
                raise Exception("Could not load model {}".format(name))

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
        model = self.models.get(model_name, {}).get("instance", None)
        if model is None:
            raise ValueError("The specified model was not found.")

        # Parse prediction request data
        incoming = self._parse_request(request_data)

        # Generate a prediction
        prediction = model.predict(incoming)
        prediction = np.atleast_2d(prediction).reshape(len(incoming), -1)
        prediction = prediction.tolist()
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
    return Response(json.dumps(model_index), mimetype="application/json")


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
