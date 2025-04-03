![Build Status](https://github.com/profitopsai/ProRCA/actions/workflows/ci.yml/badge.svg)
![PyPI](https://badge.fury.io/py/prorca.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
[![Documentation Status](https://readthedocs.org/projects/prorca/badge/?version=latest)](https://prorca.readthedocs.io/en/latest/?badge=latest)

![Logo](https://i.postimg.cc/L87fQdGG/Final-Logo.jpg)

# ProRCA: A Causal Pathway Approach for Complex Operational Environments

## Overview

**ProRCA** is an end-to-end framework for diagnosing anomalies in complex operational environments by uncovering multi-hop causal pathways. Unlike traditional anomaly detection methods that focus on correlations or feature importance (e.g., via SHAP), our approach leverages structural causal modeling to trace the full causal chain—from hidden root causes to observed anomalies.

Inspired by the paper:

> **Beyond Traditional Problem-Solving: A Causal Pathway Approach for Complex Operational Environments**  
> _Ahmed Dawoud & Shravan Talupula, February 9, 2025_ [📄 Download PDF](https://arxiv.org/abs/2503.01475)
>
> This work introduces a methodology that combines conditional anomaly scoring with causal path discovery and ranking. By extending the [DoWhy](https://github.com/py-why/dowhy) library, the framework provides decision-makers with actionable insights into the true source of complex operational disruptions.

## Features

*   **Pinpoint Critical Anomalies:** Don't just find outliers; identify the significant operational hiccups in your time series data that truly matter. ProRCA uses robust detection methods to flag the starting points for your investigation.

*   **Map Your System's Causal DNA:** Go beyond black boxes. Explicitly define and model the cause-and-effect relationships within your operations using Structural Causal Models (SCMs). This captures the real logic of how different parts of your system influence each other.

*   **Uncover the *Real* Root Causes:** This is where ProRCA shines. Move past simple correlations and discover the *actual* causal pathways leading to anomalies. Our analysis traces disruptions back through multiple steps (multi-hop paths) in your system, uniquely combining structural knowledge with noise pattern analysis to pinpoint the true origins.

*   **Visualize Causal Stories:** Complex findings become clear insights. ProRCA generates intuitive diagrams of the discovered causal pathways, making it easy to see the chain of events, understand the flow of influence, and communicate exactly where the problem started.

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
│   ├── anomaly/
│   │   ├── __init__.py
│   │   └── adtk.py
│   ├── data_generators/
│   │   ├── __init__.py
│   │   └── synthetic_sales_data.py
│   └── prorca/
│       ├── __init__.py
│       ├── dag_builder.py
│       └── pathway.py
```

## Installation

Install dependencies:

```bash
pip install profitops-rca
```

## Usage

### 1. Generate Synthetic Data

```python
from data_generators.synthetic_sales_data import generate_fashion_data_with_brand, inject_anomalies_by_date

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
from anomaly.adtk import AnomalyDetector

detector = AnomalyDetector(df_anomalous, date_col="ORDERDATE", value_col="PROFIT_MARGIN")
anomalies = detector.detect()
anomaly_dates = detector.get_anomaly_dates()

detector.visualize(figsize=(12, 6), ylim=(40, 60))
```

### 4. Build the Structural Causal Model (SCM)

```python
from prorca.pathway import ScmBuilder

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
from prorca.pathway import CausalRootCauseAnalyzer

analyzer = CausalRootCauseAnalyzer(scm, min_score_threshold=0.8)
results = analyzer.analyze(df_anomalous, anomaly_dates, start_node='PROFIT_MARGIN')
```

### 6. Visualize Causal Pathways

```python
from prorca.pathway import CausalResultsVisualizer

visualizer = CausalResultsVisualizer(analysis_results=results)
visualizer.plot_root_cause_paths()
```

![RCA Pathways](https://github.com/profitopsai/ProRCA/blob/master/docs/research%20paper/results/output.png)

![RCA Pathways](https://github.com/profitopsai/ProRCA/blob/master/docs/research%20paper/results/Dates.png)
