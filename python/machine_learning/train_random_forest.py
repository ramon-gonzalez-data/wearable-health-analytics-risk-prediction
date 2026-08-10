import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

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

RF_CONFUSION_MATRIX_PATH = OUTPUT_DIR / "rf_confusion_matrix.csv"
FEATURE_IMPORTANCE_PATH = OUTPUT_DIR / "rf_feature_importance.csv"
CLASSIFICATION_REPORT_PATH = OUTPUT_DIR / "rf_classification_report.csv"
MODEL_ACCURACY_REPORT_PATH = OUTPUT_DIR / "rf_model_accuracy.csv"


#-------------------
# 1. Read CSV file
#--------------------
dataframe = pd.read_csv(INPUT_PATH) # read the member_ml_dataset

print("Dataset shape:") #The dataset shows 100 members and 19 possible variables
print(dataframe.shape)

# Check dataset class-balance 
print("\nRisk level distribution:") 
print(dataframe["risk_level"].value_counts())  # The dataset is kind of imbalanced. Medium has many more examples than Low



#---------------------------------------
# 2. Prepare features(x) and target(y)
#---------------------------------------

# 11 health features
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

# Target column is risk_level
target = "risk_level"

# X = model inputs
X = dataframe[features]

# y = target column in a dataframe. We have one target value for every row in the dataset
y = dataframe[target]


# =========================================================
# 3. split data into training (70%) and testing (30%) sets
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,                  # features
    y,                  # target
    test_size=0.30,     # 70% train - 30% test
    random_state=42,    # Reproducible results using convention (as seed), in this case 42
    stratify=y          # Due to class-imbalace we are enable stratify = yes in order to preserve class ratios
)

# Check number of rows of training members and testing member
print("\nTraining rows:", X_train.shape[0])  
print("Testing rows:", X_test.shape[0])


# =========================
# 4. Train Random Forest
# =========================

# Prepare the model
model = RandomForestClassifier(
    n_estimators=100,             # Pick 100 trees. More trees means more stable predictions, less overfitting.
    random_state=42,              # Because random forest uses randomness internally, we fix it for reproducibility and get same result every time.
    class_weight="balanced"       # Without class_weight, the model will tend to focus on the biggest class like High risks 
)

# Train the model on the training data
model.fit(X_train, y_train)

# =========================
# 5. Evaluate model
# =========================
# Make predictions on the 30 members that the model did not train on
# X_Test does not contain risk level. The model will predict it.
y_pred = model.predict(X_test)

# Evaluate performance
print("\nAccuracy:")
rf_model_accuracy = accuracy_score(y_test, y_pred)
print(rf_model_accuracy)

# From python dictionary to Dataframe for accuracy result convertion
rf_model_accuracy_dataframe = pd.DataFrame( {
    "model": ["Random Forest"],
    "accuracy": [rf_model_accuracy]
})

# Save accuracy result
rf_model_accuracy_dataframe.to_csv(MODEL_ACCURACY_REPORT_PATH , index=False)


print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Retrieve info in a dictionary format
rf_classification_report = classification_report(
    y_test,
    y_pred,
    output_dict=True
)

# Convert dictionary into a DataFrame
rf_classification_report_dataframe = pd.DataFrame(
    rf_classification_report
).transpose()

# Take off (drop) accuracy from report and store in a .csv file
rf_classification_report_dataframe = (rf_classification_report_dataframe.drop(index = "accuracy"))
rf_classification_report_dataframe.to_csv(CLASSIFICATION_REPORT_PATH, index=True)

# =========================
# 6. Confusion matrix
# =========================

# The row labes will be:
labels = ["Low", "Medium", "High"]

# Compute the raw Confusion Matrix
cm = confusion_matrix(y_test, y_pred, labels=labels)

print("\nConfusion Matrix:")
confusion_matrix_dataframe = pd.DataFrame(cm, index=labels, columns=labels)

# Print confusion matrix and store in a .csv file
print(confusion_matrix_dataframe)
confusion_matrix_dataframe.to_csv(RF_CONFUSION_MATRIX_PATH, index=True) # Dataframe will be saved in a .csv file

# =========================
# 7. Feature importance
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


