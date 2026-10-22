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

The dashboard frontend is already connected to Flask: `gridbalance/templates/index.html`
renders each pipeline page, and `gridbalance/static/style.css` provides its styling.
No separate frontend server is needed.

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
   `requirements.txt`, `main.py`, and the `gridbalance/` folder at the repository
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
branch. Ensure the large dataset files in `gridbalance/` are included; they are
used by the deployed app.

To read the pipeline output in the console instead of the browser, run the
walkthrough script:

```
python gridbalance/main.py
```

If you run `gridbalance/App.py` directly in PyCharm, set the working directory
to `gridbalance` so Flask can find `templates/` and `static/`. The root
`main.py` handles this for you.

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

The 12 regional CSVs (`*_hourly.csv`) live directly in `gridbalance/`. Two
combined files derive from them:

- `est_hourly.parquet` — the wide archive with every regional series side by
  side, loaded through `pyarrow` (falls back to `pjm_hourly_est.csv`).
- `all_hourly_long.parquet` — the long-format master: one row per region per
  hour (`Region`, `Region_Label`, `Datetime`, `Demand_MW`), built once and
  cached. It drives the `/network` page.

## Modules

| File | Responsibility |
| --- | --- |
| `gridbalance/App.py` | Flask app, routes, global stats context |
| `gridbalance/load_data.py` | Regional, combined, and long master archive loading |
| `gridbalance/eda_charts.py` | Inline SVG chart engine (line, bar, donut, heatmap, multi-line) |
| `gridbalance/network_overview.py` | Cross-region summary and charts for `/network` |
| `gridbalance/preprocessing.py` | Cleaning and feature engineering |
| `gridbalance/model_training.py` | Model fitting, baselines, metrics, benchmark cache |
| `gridbalance/prediction.py` | Recursive forecasting |
| `gridbalance/anomaly_detection.py` | Anomaly rules |
| `gridbalance/main.py` | Console walkthrough |
| `gridbalance/templates/index.html` | Single server-rendered template |
| `gridbalance/static/style.css` | Dashboard styling |

## Notes

- Model benchmarks are cached per region, so revisiting the training page for a
  region you already ran returns immediately.
- `gridbalance/_old_3d_backup/` holds the previous FastAPI and Three.js
  implementation. It is not used by the current app.