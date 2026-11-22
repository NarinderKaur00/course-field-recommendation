# How to run this project

## 1. Environment

The project needs ZenML plus the ML libraries. A virtual environment is already
set up at `C:\Users\HP\co544venv`.

> Note: the venv is kept **outside** the project folder on purpose. This folder's
> path is long enough that creating a venv inside it fails on Windows with
> `[WinError 206] The filename or extension is too long`.

To recreate it from scratch:

```powershell
python -m venv C:\co544venv
C:\co544venv\Scripts\python.exe -m pip install "zenml[server]" -r requirements.txt
```

## 2. Initialise ZenML (once per clone)

```powershell
C:\Users\HP\co544venv\Scripts\zenml.exe init
```

## 3. Run the pipelines

```powershell
$env:PYTHONIOENCODING = "utf-8"   # avoids a cp1252 console crash on Windows

C:\Users\HP\co544venv\Scripts\python.exe run_xgb_pipeline.py
C:\Users\HP\co544venv\Scripts\python.exe run_SVM_pipeline.py
C:\Users\HP\co544venv\Scripts\python.exe run_MLP_pipeline.py
```

| Pipeline | Task | Runtime |
| --- | --- | --- |
| `run_xgb_pipeline.py` | XGBoost classifier per 5th-year subject | ~1.5 min |
| `run_SVM_pipeline.py` | Linear regression baseline on raw marks | ~20 s |
| `run_MLP_pipeline.py` | MLP classifier + grid search per subject | ~4 min |

## 4. ZenML dashboard

```powershell
C:\Users\HP\co544venv\Scripts\zenml.exe login --local --blocking
```

Then open <http://127.0.0.1:8237>. The `--blocking` flag is required: ZenML
cannot run its server as a background daemon on Windows.

Leave that terminal open and run the pipelines from a second terminal to watch
runs, steps and artifacts appear live.

## 5. Listing runs from the CLI

```powershell
$env:PYTHONIOENCODING = "utf-8"
C:\Users\HP\co544venv\Scripts\zenml.exe pipeline runs list
```

## 6. Comparing model results

After running the XGB and MLP pipelines, this reads the evaluation artifacts
back out of the ZenML store and prints a side-by-side table:

```powershell
$env:PYTHONIOENCODING = "utf-8"
C:\Users\HP\co544venv\Scripts\python.exe compare_results.py
```

## 7. Caching note

All three data-loading steps use `@step(enable_cache=False)`, so every run
recomputes and prints its metrics. Without this ZenML reuses cached artifacts
and the pipeline prints `All steps of the pipeline run were cached` with no
numbers -- correct behaviour, but not useful for a live demo.
