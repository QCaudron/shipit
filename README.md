# ShipIt

ShipIt deploys your machine learning models behind a simple API.

### Making predictions from your models

First, ensure your features is a `(n_samples, n_features)`-shaped numpy array ( in standard `sklearn` form ). Turn this into a list ( so that we can JSON-serialise it ). Then, hit `/prediction/<model_name>` with a POST request, including an `application/json` payload of `{"X": my_features_list}`. Here, `<model_name>` is the filename of the model you want to use for predicting, without the extension ( so if you has a model called `sklearn_random_forest.pkl`, you could hit `/prediction/sklearn_random_forest` ).

### Saving models

Models from `scikit-learn` should be saved with `joblib`, and have filenames starting in `sklearn_`. Models from `keras` should be saved with `model.save()` and have filenames starting in `keras_`. Simply place these files in the `models/` directory.

### To Do

- Authentication
- Better error handling
