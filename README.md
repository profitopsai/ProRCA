# ProRca: A Causal Pathway Approach for Complex Operational Environments

## Overview

![Build Status](https://github.com/profitopsai/ProRCA/actions/workflows/ci.yml/badge.svg)

**ProRca** is an end-to-end framework for diagnosing anomalies in complex operational environments by uncovering multi-hop causal pathways. Unlike traditional anomaly detection methods that focus on correlations or feature importance (e.g., via SHAP), our approach leverages structural causal modeling to trace the full causal chain—from hidden root causes to observed anomalies.

Inspired by the paper:

> **Beyond Traditional Problem-Solving: A Causal Pathway Approach for Complex Operational Environments**  
> _Ahmed Dawoud & Shravan Talupula, February 9, 2025_ [📄 Download PDF](https://arxiv.org/abs/2503.01475)
>
> This work introduces a methodology that combines conditional anomaly scoring with causal path discovery and ranking. By extending the [DoWhy](https://github.com/py-why/dowhy) library, the framework provides decision-makers with actionable insights into the true source of complex operational disruptions.

## Features

- **Anomaly Detection:**  
  Detect anomalies in time series data using ADTK’s `InterQuartileRangeAD` via the `AnomalyDetector` class.

- **Synthetic Data Generation:**  
  Generate realistic synthetic transactional data with adjustable parameters using `create_synthetic_data.py`.

- **Structural Causal Modeling:**  
  Build a causal graph and fit a Structural Causal Model (SCM) using `ScmBuilder` in the `pathway.py` module.

- **Causal Root Cause Analysis:**  
  Discover and rank multi-hop causal pathways using `CausalRootCauseAnalyzer`, which combines structural and noise-based anomaly scoring.

- **Visualization:**  
  Visualize causal pathways with Graphviz diagrams, using gradient backgrounds to indicate path importance via `CausalResultsVisualizer`.

- **End-to-End Example:**  
  A complete example of the workflow is provided in the Jupyter Notebook `notebooks/test.ipynb`.

## Project Structure

```
ProRCA/
├── .gitignore
├── .github/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── docs/
│   ├── Examples/
│   │   ├── Example_1/
│   │   └── Example_2/
│   └── research_paper/
├── pyproject.toml
├── src/
│   └── prorca/
│       ├── __init__.py
│       ├── anomaly.py
│       ├── create_synthetic_data.py
│       ├── dag_builder.py
│       ├── pathway.py
```

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/causal-rca.git
cd causal-rca
pip install -r requirements.txt
```

## Usage

### 1. Generate Synthetic Data

```python
from src.create_synthetic_data import generate_fashion_data_with_brand

df = generate_fashion_data_with_brand(start_date="2023-01-01", end_date="2023-12-31")
```

### 2. Inject Anomalies

```python
from src.create_synthetic_data import inject_anomalies_by_date

anomaly_schedule = {
    '2023-06-10': ('ExcessiveDiscount', 0.8),
    '2023-06-15': ('COGSOverstatement', 0.4),
    '2023-07-01': ('FulfillmentSpike', 0.5)
}

df_anomalous = inject_anomalies_by_date(df, anomaly_schedule)
```

### 3. Detect Anomalies

```python
from src.anomaly import AnomalyDetector

detector = AnomalyDetector(df_anomalous, date_col="ORDERDATE", value_col="PROFIT_MARGIN")
anomalies = detector.detect()
anomaly_dates = detector.get_anomaly_dates()

detector.visualize(figsize=(12, 6), ylim=(40, 60))
```

### 4. Build the Structural Causal Model (SCM)

```python
from src.pathway import ScmBuilder

edges = [
    ("PRICEEACH", "UNIT_COST"), ("PRICEEACH", "SALES"),
    ("UNIT_COST", "COST_OF_GOODS_SOLD"),
    ("QUANTITYORDERED", "SALES"), ("QUANTITYORDERED", "COST_OF_GOODS_SOLD"),
    ("SALES", "DISCOUNT"), ("SALES", "NET_SALES"),
    ("DISCOUNT", "NET_SALES"),
    ("NET_SALES", "FULFILLMENT_COST"), ("NET_SALES", "MARKETING_COST"),
    ("NET_SALES", "RETURN_COST"), ("NET_SALES", "PROFIT"),
    ("FULFILLMENT_COST", "PROFIT"), ("MARKETING_COST", "PROFIT"),
    ("RETURN_COST", "PROFIT"), ("COST_OF_GOODS_SOLD", "PROFIT"),
    ("SHIPPING_REVENUE", "PROFIT"), ("PROFIT", "PROFIT_MARGIN"),
    ("NET_SALES", "PROFIT_MARGIN")
]

nodes = ["PRICEEACH", "UNIT_COST", "SALES", "COST_OF_GOODS_SOLD", "PROFIT_MARGIN"]

builder = ScmBuilder(edges=edges, nodes=nodes)
scm = builder.build(df_anomalous)
```

### 5. Perform Causal Root Cause Analysis

```python
from src.pathway import CausalRootCauseAnalyzer

analyzer = CausalRootCauseAnalyzer(scm, min_score_threshold=0.8)
results = analyzer.analyze(df_anomalous, anomaly_dates, start_node='PROFIT_MARGIN')
```

### 6. Visualize Causal Pathways

```python
from src.pathway import CausalResultsVisualizer

visualizer = CausalResultsVisualizer(analysis_results=results)
visualizer.plot_root_cause_paths()
```

![RCA Pathways](https://github.com/profitopsai/ProRCA/blob/master/docs/research%20paper/results/output.png)

![RCA Pathways](https://github.com/profitopsai/ProRCA/blob/master/docs/research%20paper/results/Dates.png)

### 7. Run the End-to-End Example

Open `notebooks/test.ipynb` in Jupyter to see the complete workflow.
