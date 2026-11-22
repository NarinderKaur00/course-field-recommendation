from steps_new.load_data import load_data
from steps_new.preprocess_data import preprocess_data
from steps.train_RF import train_RF
from steps.evaluate_RF import evaluate_RF
from zenml import pipeline

@pipeline
def RF_pipeline(data_path: str):
    """
    Ingest data, preprocess, train and evaluate Random Forest model.
    """
    df = load_data(data_path)
    features, targets = preprocess_data(df)
    train_results_dict = train_RF(features, targets)
    evaluate_RF(train_results_dict)
