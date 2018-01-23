from flask import Flask, request
from shipit import ShipIt


# Instantiate ShipIt object
shipit = ShipIt()

# Spin up Flask app
app = Flask(__name__)


# Are we live ?
@app.route("/")
def index():
	return "Hello !"


# Prediction endpoint
@app.route("/predict/<model_name>", methods=["POST"])
def predict(model_name):

	# Generate a prediction
	try:
		return shipit.predict(model_name, request.get_json())

	except:
		raise


if __name__ == "__main__":
	app.run()
