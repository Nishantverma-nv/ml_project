# Grid Balance Project

Hourly electricity load forecasting and anomaly detection for 12 PJM regions,
presented as a staged Flask dashboard.

## Requirements

- Python 3.13

## Setup

Install the dependencies into the project virtual environment:

```
python -m pip install -r requirements.txt
```

PyCharm is already configured to use `.venv` as the project interpreter.

Run the focused tests from the project root with:

```powershell
python -m unittest discover -s tests -v
```

## Running the app

From the `grpproject` folder:

```
python main.py
```

Then open <http://127.0.0.1:5005>.

Port notes: Grid Balance uses port **5005** by default so it never clashes
with the PlacementPrediction project, which listens on **5000**. To run
Grid Balance on another port:

```
set GRIDBALANCE_PORT=5001
python main.py
```

Then open <http://127.0.0.1:5001>.

## Project structure

- `frontend/templates/` and `frontend/static/` contain the dashboard UI and styles.
- `backend/` contains the Flask app, forecasting/data-processing modules, and `data/`
  with the regional CSV and combined archives.
- The Flask backend serves the frontend from its separate folder on the same origin;
  no separate frontend server or CORS configuration is needed.
- `legacy/old_3d_backup/` preserves the unused earlier FastAPI/Three.js prototype.

## Deploying to Render with Docker

### Test the container locally

Install and start Docker Desktop, then run these commands from the project root:

```powershell
docker build -t gridbalance .
docker run --rm -p 10000:10000 -e PORT=10000 gridbalance
```

Open <http://127.0.0.1:10000>. Stop the container with `Ctrl+C`.

### Deploy on Render

1. Push this project to a GitHub repository. Keep `Dockerfile`, `.dockerignore`,
   `requirements.txt`, `main.py`, `backend/`, and `frontend/` at the repository
   root. The included `.gitignore` keeps local virtual environments and IDE files
   out of the GitHub upload.
2. In Render, choose **New + → Web Service**, then connect the GitHub repository
   and select the branch to deploy.
3. Set **Root Directory** to the repository root (leave it blank if the project
   files are at the root), and choose **Docker** as the runtime.
4. Use the included root `Dockerfile`. Leave the Docker build context at the
   repository root. Do not enter separate build or start commands.
5. Choose a service name, region, and plan, then click **Deploy Web Service**.
   Render builds the image, starts Gunicorn, and provides the `PORT` environment
   variable automatically. No additional environment variables are required.
6. When the first deploy is marked **Live**, open the `onrender.com` URL Render
   shows for the service. You can also open `/data-loading`, `/forecast`, or
   `/anomaly-detection` to check the other dashboard pages.

If you have not pushed to GitHub before, create an empty repository there, then
use GitHub Desktop to add this project folder, commit the files, and publish the
branch. Ensure the dataset files in `backend/data/` are included; they are used
by the deployed app.

To read the pipeline output in the console instead of the browser, run the
walkthrough script:

```
python backend/main.py
```

If you run `backend/App.py` directly in PyCharm, the frontend and data paths are
resolved from the project root. The root `main.py` is the recommended launcher.

## Stages

| Route | Purpose |
| --- | --- |
| `/` | Hero overview, pipeline stages, and the 12 regional files |
| `/data-loading` | Per-region row counts, ranges, gaps, and both combined archives |
| `/preprocessing` | Cleaning results and 21 engineered features |
| `/eda-analysis` | Nine SVG charts: line, bar, histogram, box plot, scatter, heatmap, donut |
| `/network` | Cross-region charts from the combined long archive |
| `/model-training` | Four regressors benchmarked against mean and naive baselines |
| `/forecast` | Recursive hourly demand forecasts from a chosen start hour |
| `/anomaly-detection` | Robust-z outliers, stuck meters, and impossible readings |

Every stage has a region picker, so you can walk a single region through the
full pipeline.

## Datasets

The 12 regional CSVs (`*_hourly.csv`) live in `backend/data/`. Two combined
files derive from them:

- `est_hourly.parquet` — the wide archive with every regional series side by
  side, loaded through `pyarrow` (falls back to `pjm_hourly_est.csv`).
- `all_hourly_long.parquet` — the long-format master: one row per region per
  hour (`Region`, `Region_Label`, `Datetime`, `Demand_MW`), built once and
  cached. It drives the `/network` page.

## Modules

| File | Responsibility |
| --- | --- |
| `backend/App.py` | Flask app, routes, global stats context |
| `backend/load_data.py` | Regional, combined, and long master archive loading |
| `backend/eda_charts.py` | Inline SVG chart engine (line, bar, donut, heatmap, multi-line) |
| `backend/network_overview.py` | Cross-region summary and charts for `/network` |
| `backend/preprocessing.py` | Cleaning and feature engineering |
| `backend/model_training.py` | Model fitting, baselines, metrics, benchmark cache |
| `backend/prediction.py` | Recursive forecasting |
| `backend/anomaly_detection.py` | Anomaly rules |
| `backend/main.py` | Console walkthrough |
| `frontend/templates/index.html` | Single server-rendered template |
| `frontend/static/style.css` | Dashboard styling |

## Notes

- Model benchmarks are cached per region, so revisiting the training page for a
  region you already ran returns immediately.
- `legacy/old_3d_backup/` holds the previous FastAPI and Three.js
  implementation. It is not used by the current app.