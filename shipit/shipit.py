import json
from glob import glob
from importlib import import_module

import numpy as np


class ShipIt:

	def __init__(self):
		"""
		Load all sklearn and keras models into RAM.
		"""

		# Load all models
		models = {}
		keras_models = glob("models/keras_*") 
		sklearn_models = glob("models/sklearn_*")

		# If we have keras models to load, import the right function
		if keras_models:
			from keras.models import load_model

		# Same with sklearn
		if sklearn_models:
			from sklearn.externals import joblib

		# Import all models, storing them in a dict with their filename as key
		for filename in keras_models:
			models[filename.split(".")[0]] = load_model(filename)
		for filename in sklearn_models:
			models[filename.split(".")[0]] = joblib.load(filename)

		self.models = models

	def predict(self, model_name, json_data):
		"""
		Given a model name and the JSON bundle from the API request,
		make predictions and return them in JSON form.
		"""

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

	def generate_requirements(self, filepath):
		"""
		Generate a requirements.txt file. Run this from within the envinronment in
		which you saved your models, to ensure all packages have the same versions.
		"""
		
		required_versions = []
		required_packages = {
			"flask": "Flask",
			"numpy": "numpy",
			"scipy": "scipy",
			"sklearn": "scikit-learn",
			"tensorflow": "tensorflow",
			"keras": "keras",
			"h5py": "h5py"
		}

		for package, package_name in required_packages.items():
			version = import_module("{}".format(package)).__version__
			required_versions.append("{}=={}\n".format(package_name, version))

		with open(filepath + "/requirements.txt", "w") as f:
			for line in required_versions:
				f.write(line)

	def _parse_request(self, json_data):
		"""
		Parse the JSON request and return it in numpy form. Validation occurs here.
		"""

		X = json_data.get("X", None)

		try:
			X = np.array(X)  # numpyify
			assert len(X.shape) == 2  # X.shape should be (n_samples, n_features)

		except:
			print("Could not parse JSON data.")
			raise

		return X