import json
from glob import glob

import numpy as np
from sklearn.externals import joblib
from keras.models import load_model


class ShipIt:

	def __init__(self):

		# Load all models
		models = {}
		keras_models = glob("models/keras_*") 
		sklearn_models = glob("models/sklearn_*")

		for filename in keras_models:
			models[filename.split(".")[0]] = load_model(filename)
		for filename in sklearn_models:
			models[filename.split(".")[0]] = joblib.load(filename)

		self.models = models

	def predict(self, model_name, json_data):

		# Grab the correct model object
		model = self.models.get(model_name, None)
		if model is None:
			raise ValueError("The specified model was not found.")

		# Parse prediction request data
		X = self._parse_request(json_data)
		if X is None:
			raise ValueError("Request data could not be parsed.")

		# Generate a prediction
		try:
			prediction = np.atleast_2d(model.predict(X)).reshape(len(X), -1)
			return json.dumps({"prediction": prediction.tolist()})

		except:
			print("Could not generate a prediction.\n")
			raise

	def _parse_request(self, json_data):

		X = json_data.get("X", None)

		try:
			X = np.array(X)  # numpyify
			assert len(X.shape) == 2  # X.shape should be (n_samples, n_features)

		except:
			print("Could not parse JSON data.")
			raise

		return X