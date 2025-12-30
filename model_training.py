import numpy as np
from sklearn.linear_model import LinearRegression

# Train a simple model (example data)
X = np.array([
    [75.0, 18, 30],
    [70.0, 21, 25],
    [80.0, 15, 35],
    [65.0, 24, 20]
])

y = np.array([78.0, 75.0, 82.0, 70.0])

model = LinearRegression()
model.fit(X, y)

# THIS FUNCTION IS WHAT GUI WILL USE
def predict_cwa(current_cwa, credit_load, study_hours):
    input_data = np.array([[current_cwa, credit_load, study_hours]])
    prediction = model.predict(input_data)
    return round(prediction[0], 2)
