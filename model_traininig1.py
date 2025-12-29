""""
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import  r2_score
from pathlib import Path

BASE_DIR = Path(_file_).resolve().parent
sample_path = BASE_DIR / "sample.txt"


if sample_path.exists():
    df = pd.read_csv(sample_path)
    df.columns = df.columns.str.strip().str.lower()
    #print(df.columns)
    #print(df.dropna())
    #print(df.head())
    #print(df.isnull().sum())

    x = df[["current_cwa" , "study_hours" , "credit_hours"]] # Feature
    y = df["final_cwa"] # Target

    #print(x.shape)
    #print(y.shape)

    x_train, x_test, y_train , y_test =train_test_split (x, y , test_size=0.2 , random_state=42)

    model = LinearRegression()
    model.fit(x_train , y_train)
    coefficients = pd.Series(model.coef_, index=x.columns)
    print(coefficients)
    #print("Intercept:", model.intercept_)

    print("Intercept:", model.intercept_)
    print(pd.Series(model.coef_, index=x.columns))

    
    #from sklearn.metrics import r2_score

    y_pred = model.predict(x_test)
    r2 = r2_score(y_test, y_pred)
    print("R² score:", r2)

    new_student = pd.DataFrame([[75.5, 25, 18]], columns=x.columns)  # current_cwa, study_hours, credit_hours
    predicted_cwa = model.predict(new_student)
    print("Predicted Final CWA:", predicted_cwa[0])
else:
    print(f"File not found at {cwa_data_path}. Please verify the location.")

"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import  accuracy_score
from pathlib import Path

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sample_path = BASE_DIR / "sample.txt"



if sample_path.exists():
    df = pd.read_csv(sample_path)
    df.columns = df.columns.str.strip().str.lower()
    #print(df.columns)
    print(df.dropna())
    #print(df.head())
    #print(df.isnull().sum())
    df["success"] = (df["final_cwa"] >= df["target_cwa"]) .astype(int)
    print(df)
      
    x = df[["current_cwa", "study_hours", "credit_hours", "target_cwa"]] # Feature
    y = df["success"] # Target

    #print(x.shape)
    #print(y.shape)

    x_train, x_test, y_train , y_test =train_test_split (x, y , test_size=0.2 , random_state=42)

    model = LogisticRegression()
    model.fit(x_train , y_train)
    
    y_pred = model.predict(x_test)

    y_prob = model.predict_proba(x_test)
    
    accuracy = accuracy_score(y_pred , y_prob)
    print("Accuracy:", accuracy)
    
    odds_ratios = pd.Series(np.exp(model.coef_[0]), index=x.columns)
    print("\nOdds Ratios (Effect on success):")
    print(odds_ratios)

    new_student = [[75.5, 25, 18, 78]]

# Predict probability of success
    success_probability = model.predict_proba(new_student)[0][1]

    
    print("\nPredicted probability of success:", success_probability)

else:
    print("File not found" )