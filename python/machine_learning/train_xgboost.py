from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score,classification_report,confusion_matrix)
from xgboost import XGBClassifier


# =========================
# Input Path
# =========================
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = (REPO_ROOT/"data"/"processed"/"member_ml_dataset.csv")

# =========================
# Output Path
# =========================
OUTPUT_DIR = (REPO_ROOT / "data" / "ml_results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
XGB_CONFUSION_MATRIX_PATH = OUTPUT_DIR / "xgboost_confusion_matrix.csv"
FEATURE_IMPORTANCE_PATH = OUTPUT_DIR / "xgboost_feature_importance.csv"
CLASSIFICATION_REPORT_PATH = OUTPUT_DIR / "xgboost_classification_report.csv"
MODEL_ACCURACY_REPORT_PATH = OUTPUT_DIR / "xgboost_model_accuracy.csv"
# =========================
# Read Dataset
# =========================

dataframe = pd.read_csv(INPUT_PATH)
print("Dataset shape:")
print(dataframe.shape)

print("\nRisk Level Distribution:")
print(dataframe["risk_level"].value_counts())


# =========================
# Features and Target
# =========================

features = [
    "age",
    "avg_heart_rate",
    "max_heart_rate",
    "avg_systolic_bp",
    "max_systolic_bp",
    "avg_diastolic_bp",
    "max_diastolic_bp",
    "avg_glucose",
    "max_glucose",
    "avg_spo2",
    "min_spo2"
]

target = "risk_level"

X = dataframe[features]

y_text = dataframe[target]


# =========================
# Encode Target (XGBoost works better with numeric labels)
# =========================
# LabelEncoder usually sorts alphabetically:
# High   -> 0
# Low    -> 1
# Medium -> 2

label_encoder = LabelEncoder()          # Converts text label into numbers
y = label_encoder.fit_transform(y_text) # converts the text into numeric classes

print("\nEncoded Classes:")
for number, class_name in enumerate(label_encoder.classes_):
    print(number, "=", class_name)


# =========================
# Train / Test Split
# =========================
# The train/test split is the same as we did in Random Forest
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

print("\nTraining rows:", X_train.shape[0])
print("Testing rows:", X_test.shape[0])


# =========================
# Train XGBoost Model
# =========================

model = XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    random_state=42,
    eval_metric="mlogloss"
)

model.fit(X_train, y_train)


# =========================
# Make Predictions
# =========================

y_pred = model.predict(X_test)


# =========================
# Decode Predictions
# =========================
# Convert numbers back to original labels:
# 0, 1, 2 -> High, Low, Medium

y_test_text = label_encoder.inverse_transform(y_test)
y_pred_text = label_encoder.inverse_transform(y_pred)


# =========================
# Evaluate Model
# =========================

xgb_model_accuracy  = accuracy_score(y_test_text, y_pred_text)

print("\nAccuracy:")
print(xgb_model_accuracy)

# From python dictionary to Dataframe for accuracy result convertion
xgb_model_accuracy_dataframe = pd.DataFrame( {
    "model": ["XGBoost"],
    "accuracy": [xgb_model_accuracy]
})

# Save accuracy result
xgb_model_accuracy_dataframe.to_csv(MODEL_ACCURACY_REPORT_PATH , index=False)



print("\nClassification Report:")
print(classification_report(y_test_text, y_pred_text))

#Before creating the report, we will convert the numbers back:
# 0 -> High
# 1 -> Low
# 2 -> Medium

y_test_text = label_encoder.inverse_transform(y_test)
y_pred_text = label_encoder.inverse_transform(y_pred)

# Retrieve info in a dictionary format
xgb_classification_report = classification_report(
    y_test_text,
    y_pred_text,
    output_dict=True
)

# Convert dictionary into a DataFrame
xgb_classification_report_dataframe = pd.DataFrame(
    xgb_classification_report
).transpose()

# Take off (drop) accuracy from report and store in a .csv file
xgb_classification_report_dataframe = (xgb_classification_report_dataframe.drop(index = "accuracy"))
xgb_classification_report_dataframe.to_csv(CLASSIFICATION_REPORT_PATH, index=True)

# =========================
# Confusion Matrix
# =========================

labels = ["Low", "Medium", "High"]

confusion_matrix_result = confusion_matrix(
    y_test_text,
    y_pred_text,
    labels=labels
)

confusion_matrix_dataframe = pd.DataFrame(
    confusion_matrix_result,
    index=labels,
    columns=labels
)

print("\nConfusion Matrix:")
print(confusion_matrix_dataframe)
confusion_matrix_dataframe.to_csv(XGB_CONFUSION_MATRIX_PATH, index=True) # Dataframe will be saved in a .csv file


# =========================
# Feature Importance
# =========================

feature_importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance:")
print(feature_importance)

#Save Result to csv
feature_importance.to_csv(FEATURE_IMPORTANCE_PATH, index=False)


