# Random Forest Exoplanet Classification

This directory contains a Jupyter notebook implementing a Random Forest model for classifying exoplanet candidates using Kepler Objects of Interest (KOI) data.

## Contents

- `random_forest_exoplanet_classification.ipynb`: Main notebook containing data analysis, model training and evaluation
- `exoplanet_randomforest_model.joblib`: Trained Random Forest model (after running notebook)
- `exoplanet_randomforest_scaler.joblib`: StandardScaler for preprocessing new data (after running notebook)
- `exoplanet_randomforest_feature_names.joblib`: Feature names for model input (after running notebook)
- `exoplanet_randomforest_label_encoder.joblib`: Label encoder for target variable (after running notebook)

## Dataset

The model is trained on `KOI-Playground-Train-Data.csv` from the Kepler space telescope observations.

## Model Performance

The notebook compares Random Forest with SVM and XGBoost models, analyzing:
- Classification metrics (accuracy, precision, recall, F1-score, AUC-ROC)
- Feature importance
- ROC and Precision-Recall curves
- Hyperparameter optimization

## Model Deployment

The notebook includes sample code demonstrating how to deploy the trained model for making predictions on new data.

## Requirements

- Python 3.8+
- scikit-learn
- pandas
- numpy
- matplotlib
- seaborn
- xgboost
- joblib