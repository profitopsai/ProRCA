End-to-End Example: Retail Anomaly Root Cause Analysis
=====================================================

This example demonstrates the complete ProRCA workflow, from generating synthetic data with known anomalies to identifying the causal root causes of those anomalies. It manually incorporates the steps and findings originally presented in the `Data_Generation.ipynb` and `RCA.ipynb` notebooks located in the `docs/examples/Example_1/` directory.

**Goal:** To show how ProRCA can pinpoint the source of disruptions (like excessive discounts or cost spikes) in a simulated retail environment by analyzing their impact on a key metric like Profit Margin.

**Note:** Using synthetic data here allows us to validate ProRCA's results because we know precisely which anomalies were injected. You can adapt this workflow for your own real-world data.

Step 1: Data Preparation (from `Data_Generation.ipynb`)
-------------------------------------------------------------

First, we generate a realistic synthetic dataset simulating fashion retail transactions over a year.

Generate Base Data
^^^^^^^^^^^^^^^^^^

We use the ``generate_fashion_data_with_brand`` function to create the initial dataset.

.. code-block:: python

   import pandas as pd
   from data_generators.synthetic_sales_data import generate_fashion_data_with_brand

   # Generate synthetic retail data for the year 2023
   df_synthetic = generate_fashion_data_with_brand(start_date="2023-01-01", end_date="2023-12-31")

   # This creates a DataFrame with columns like ORDERDATE, SALES, UNIT_COST, PROFIT_MARGIN, etc.
   print("Generated DataFrame sample:")
   print(df_synthetic.head())

Inject Known Anomalies
^^^^^^^^^^^^^^^^^^^^^^

Next, we inject specific anomalies using a predefined schedule with ``inject_anomalies_by_date``. This function modifies the source metric and correctly recalculates all downstream effects (like profit), which is crucial for testing causal discovery.

.. code-block:: python

   from data_generators.synthetic_sales_data import inject_anomalies_by_date

   # Define the schedule of anomalies to inject
   # Format: { 'Date': (Type, SeverityFactor, 'SimulatedCause', 'AffectedScope'), ... }
   anomaly_schedule = {
       '2023-01-10': ('ExcessiveDiscount', 0.5, 'PricingError', 'Apparel'),
       '2023-06-10': ('COGSOverstatement', -0.8, 'SupplierIssue', 'Footwear'), # Simulates 80% higher unit cost impact
       '2023-09-10': ('FulfillmentSpike', 3.0, 'LogisticsIssue', 'Beauty'), # Cost quadruples
       '2023-12-10': ('ReturnSurge', 10.0, 'QualityIssue', 'Accessories') # Cost increases 10x
   }

   # Apply the anomalies to the synthetic dataframe
   df_anomalous = inject_anomalies_by_date(df_synthetic, anomaly_schedule)

   # This df_anomalous DataFrame now contains the ground truth anomalies
   # and will be used for the rest of the analysis.
   print("\nDataFrame sample after injecting anomalies (check ANOMALY_TYPE):")
   print(df_anomalous.head())

   # For convenience in subsequent runs, this data (or an aggregated version)
   # might be saved to CSV, like 'fashion_data_with_anomalies_aggregated.csv'.
   # Here, we proceed with the df_anomalous DataFrame in memory.

   # Aggregate data daily for time series analysis (as done in RCA.ipynb)
   # Define aggregation rules (assuming these were defined earlier)
   aggregation_dict = {
       "PRICEEACH": "mean", "UNIT_COST": "mean", "QUANTITYORDERED": "sum",
       "SALES": "sum", "DISCOUNT": "sum", "NET_SALES": "sum",
       "FULFILLMENT_COST": "sum", "MARKETING_COST": "sum", "RETURN_COST": "sum",
       "COST_OF_GOODS_SOLD": "sum", "SHIPPING_REVENUE": "sum", "PROFIT": "sum",
       "PROFIT_MARGIN": "mean", "IS_MARGIN_NEGATIVE": "mean"
   }
   df_agg = df_anomalous.groupby(pd.Grouper(key='ORDERDATE', freq='D')).agg(aggregation_dict).reset_index()


Step 2: Anomaly Detection (from `RCA.ipynb`)
--------------------------------------------

We use the ``AnomalyDetector`` class to identify dates where the ``PROFIT_MARGIN`` significantly deviates from its normal pattern in the aggregated data.

.. code-block:: python

   from anomaly.adtk import AnomalyDetector

   # Initialize the detector on the aggregated anomalous data
   detector = AnomalyDetector(df_agg, date_col="ORDERDATE", value_col="PROFIT_MARGIN")

   # Run the detection
   anomaly_results_df = detector.detect()

   # Get the specific dates where anomalies were detected
   anomaly_dates = detector.get_anomaly_dates()
   print(f"\nDetected anomaly dates:\n{anomaly_dates}")

   # Visualize the anomalies (optional, shows plot)
   # detector.visualize(figsize=(14, 7), ylim=(10, 70))

Expected Output (Anomaly Dates):
The detector should identify the dates where we injected significant anomalies impacting the profit margin. Based on the `RCA.ipynb` output:

.. code-block:: text

   Detected anomaly dates:
   0   2023-01-10
   1   2023-06-10
   2   2023-09-10
   3   2023-12-10
   Name: ORDERDATE, dtype: datetime64[ns]

Step 3: Define Causal Structure (DAG) (from `RCA.ipynb`)
--------------------------------------------------------

We define the assumed causal relationships between the metrics using ProRCA's helper function ``DagBuilder``. This creates a Directed Acyclic Graph (DAG). *Alternatively, you could define these edges manually based on your specific domain knowledge.*

.. code-block:: python

   from prorca.dag_builder import DagBuilder

   # Automatically create edges based on typical retail column names in df_agg
   causal_edges = DagBuilder(df_agg.columns)
   print(f"\nGenerated {len(causal_edges)} causal edges for the DAG.")

Step 4: Build the Structural Causal Model (SCM) (from `RCA.ipynb`)
------------------------------------------------------------------

Using the defined DAG and the data, we build and fit a Structural Causal Model (SCM). The ``ScmBuilder`` automatically assigns causal mechanisms (like regression models) to represent how each variable is generated from its parents.

.. code-block:: python

   from prorca.pathway import ScmBuilder

   print("\nBuilding Structural Causal Model...")
   # Initialize the builder with the edges
   builder = ScmBuilder(edges=causal_edges, visualize=False)

   # Build and fit the SCM using the aggregated anomalous data
   scm = builder.build(df=df_agg)
   # This process involves fitting models for each node based on its parents.
   # The output during execution shows details of model selection (e.g., RidgeCV, RandomForestRegressor).
   print("SCM built and fitted.")

Step 5: Perform Causal Root Cause Analysis (from `RCA.ipynb`)
-------------------------------------------------------------

This is the core step where ``CausalRootCauseAnalyzer`` uses the fitted SCM to trace the detected anomalies (from Step 2) back to their origins along the causal paths defined in the DAG. It ranks paths based on a combination of structural and noise-based anomaly scores. We analyze each anomaly date separately using `analyze_by_date`.

.. code-block:: python

   from prorca.pathway import CausalRootCauseAnalyzer

   print("\nPerforming Causal Root Cause Analysis...")
   # Initialize the analyzer with the SCM and a score threshold
   analyzer = CausalRootCauseAnalyzer(scm, min_score_threshold=0.7)

   # Analyze each detected anomaly date individually
   analysis_results_by_date = analyzer.analyze_by_date(df_agg, anomaly_dates, start_node='PROFIT_MARGIN')

   # The analyzer prints detailed results during execution.
   # Below is a sample of the expected output for the first detected date (2023-01-10).

Expected Output Sample (for 2023-01-10):
The analysis output identifies the most likely causal pathways leading to the anomaly on the specified date, ranked by significance.

.. code-block:: text

   --- Analyzing anomaly date: 2023-01-10 00:00:00 ---
   ... (calculation logs) ...
   Found 3 potential root cause paths.

   Detailed path analysis (ordered by causal significance):
   ------------------------------------------------------------

   Path 1 (Causal Significance: 0.0871):
   ├─ PROFIT_MARGIN        (Combined Score: 0.8046, Noise Contribution: 0.0382)
     ├─ NET_SALES            (Combined Score: 0.8158, Noise Contribution: 0.0745)
       └─ DISCOUNT             (Combined Score: 0.8691, Noise Contribution: 0.1244)

   Path 2 (Causal Significance: 0.0744):
   ├─ PROFIT_MARGIN        (Combined Score: 0.8046, Noise Contribution: 0.0382)
     ├─ PROFIT               (Combined Score: 0.8280, Noise Contribution: 0.0340)
       └─ SHIPPING_REVENUE     (Combined Score: 0.7707, Noise Contribution: 0.1063)

   # ... (other paths) ...

This indicates that for the anomaly on 2023-01-10, the most significant causal path involves `DISCOUNT` -> `NET_SALES` -> `PROFIT_MARGIN`. This matches the 'ExcessiveDiscount' anomaly we injected on that date. The analysis would proceed similarly for the other dates.

Step 6: Visualize Causal Pathways (from `RCA.ipynb`)
----------------------------------------------------

Finally, we can visualize the identified pathways for a specific date using ``CausalResultsVisualizer``.

.. code-block:: python

   from prorca.pathway import CausalResultsVisualizer

   print("\nVisualizing the results for the first anomaly date...")

   # Select the results for the specific date you want to visualize
   # (Using the first detected date from Step 2 as an example)
   first_anomaly_date = anomaly_dates.iloc[0]
   results_to_visualize = analysis_results_by_date[first_anomaly_date]

   # Initialize the visualizer
   visualizer = CausalResultsVisualizer(analysis_results=results_to_visualize)

   # Plot the ranked root cause paths (generates a diagram)
   visualizer.plot_root_cause_paths()

This would generate a diagram (typically displayed inline in a notebook) showing the paths found in Step 5, often with nodes colored or sized based on their anomaly scores, making the causal flow easy to understand.

Step 7: Conclusion (Summary from `RCA.ipynb`)
---------------------------------------------

As demonstrated in the analysis (particularly Step 5's output), ProRCA successfully identified the primary causal pathways corresponding to the anomalies intentionally injected in Step 1.

* **2023-01-10:** Path involving `DISCOUNT` matches the injected `ExcessiveDiscount`.
* **2023-06-10:** Path involving `COST_OF_GOODS_SOLD` / `UNIT_COST` matches the `COGSOverstatement`.
* **2023-09-10:** Path involving `FULFILLMENT_COST` matches the `FulfillmentSpike`.
* **2023-12-10:** Path involving `RETURN_COST` matches the `ReturnSurge`.

This confirms ProRCA's ability to trace anomalies back to their root causes even within a system with complex, interacting variables, by leveraging structural causal modeling.