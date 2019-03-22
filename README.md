# ShipIt

ShipIt deploys your machine learning models behind a simple API.

## Quickstart

#. `pip install shipit`
#. `shipit init`
#. Edit the new `shipit.yml` to point to your serialized model file(s)
#. `shipit build -t yourtagname`
#. `docker run -p 5000:5000 -it yourtagname`

You now have your models being served from a web API. Visit `localhost:5000/` to see the list of available models. To get predictions from your models, send a JSON serialized array or 2d array (for multiple predictions) to the provided model's endpoint.

An example in curl to get two predictions back.

```
curl -d '[[5, 1, 6], [1, 2, 3]]' -H "Content-Type: application/json" -X POST http://localhost:5000/predict/[modelname]

"[[10, 2, 6], [2, 4, 6]]"
```

The response will always be a 2d array, so if you send one data point expect a list back with only one row.

### Formatting model data

First, ensure your features is a `(n_samples, n_features)`-shaped numpy array ( in standard `sklearn` form ). Turn this into a list ( so that we can JSON-serialise it ). 

### Saving models

Models from `scikit-learn` should be saved with `joblib`. Models from `keras` should be saved with `model.save()`. 

### To Do

- Authentication
- Better error handling
- Better readme
- Moar commentz ( and don't forget the docstrings )
- Support XGBoost models
- Figure out why sklearn.linear_model.LinearRegression can't be pickled