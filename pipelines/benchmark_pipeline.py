from steps_new.load_data import load_data
from steps_new.preprocess_data import preprocess_data
from steps.train_models import train_models
from steps.evaluate_models import evaluate_models
from zenml import pipeline

@pipeline
def benchmark_pipeline(data_path: str):
    """
    Ingest data, preprocess, then train and evaluate every classical ML model.
    """
    df = load_data(data_path)
    features, targets = preprocess_data(df)
    train_results_dict = train_models(features, targets)
    evaluate_models(train_results_dict)
