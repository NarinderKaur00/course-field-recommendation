from pipelines.RF_pipeline import RF_pipeline
import logging

if __name__ == "__main__":

    # Run the pipeline
    # Add the correct path of the file
    data_path = "./data/Grade_CS_Students.csv"
    logging.info("Starting RF pipeline")
    RF_pipeline(data_path)
