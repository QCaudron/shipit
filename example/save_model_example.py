import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.externals import joblib

# Data
x = np.linspace(0, 10, 10000).reshape(-1, 1)
y = x**2

# Model
random_forest = RandomForestRegressor(n_estimators=30)
random_forest.fit(x, y)

# Serialise
os.makedirs("models", exist_ok=True)
with open("models/sklearn_rfc.pkl", "wb") as f:
    joblib.dump(random_forest, f)