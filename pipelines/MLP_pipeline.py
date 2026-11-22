from steps_new.load_data import load_data
from steps_new.preprocess_data import preprocess_data
from steps.train_MLP import train_MLP
from steps.evaluate_MLP import evaluate_MLP
from zenml import pipeline

@pipeline
def MLP_pipeline(data_path: str):
    """
    Ingest data, preprocess, train and evaluate MLP model.
    """
    df = load_data(data_path)
    features, targets = preprocess_data(df)
    train_results_dict = train_MLP(features, targets)
    evaluate_MLP(train_results_dict)
