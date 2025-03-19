Usage
=====

This section provides a step-by-step guide to using ProRCA for anomaly detection and causal root cause analysis. The examples below demonstrate how to generate synthetic data, inject anomalies, detect them, build a structural causal model, perform root cause analysis, and visualize the results.

1. Generate Synthetic Data
--------------------------

Use the ``generate_fashion_data_with_brand`` function to create synthetic transactional data:

.. code-block:: python

   from src.data_generators.synthetic_sales_data import generate_fashion_data_with_brand

   df = generate_fashion_data_with_brand(start_date="2023-01-01", end_date="2023-12-31")

This generates a DataFrame with columns like ``ORDERDATE``, ``SALES``, ``PROFIT_MARGIN``, and more.

2. Inject Anomalies
-------------------

Inject synthetic anomalies into the data using ``inject_anomalies_by_date``:

.. code-block:: python

   from src.data_generators.synthetic_sales_data import inject_anomalies_by_date

   anomaly_schedule = {
       '2023-06-10': ('ExcessiveDiscount', 0.8),
       '2023-06-15': ('COGSOverstatement', 0.4),
       '2023-07-01': ('FulfillmentSpike', 0.5)
   }

   df_anomalous = inject_anomalies_by_date(df, anomaly_schedule)

This adds anomalies like excessive discounts or fulfillment cost spikes on specified dates.

3. Detect Anomalies
-------------------

Use the ``AnomalyDetector`` class to identify anomalies in the data:

.. code-block:: python

   from src.anomaly.adtk import AnomalyDetector

   detector = AnomalyDetector(df_anomalous, date_col="ORDERDATE", value_col="PROFIT_MARGIN")
   anomalies = detector.detect()
   anomaly_dates = detector.get_anomaly_dates()

   detector.visualize(figsize=(12, 6), ylim=(40, 60))

This detects anomalies in the ``PROFIT_MARGIN`` column and visualizes them.

4. Build the Structural Causal Model (SCM)
------------------------------------------

Define a causal graph and build an SCM using ``ScmBuilder``:

.. code-block:: python

   from src.prorca.pathway import ScmBuilder

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

5. Perform Causal Root Cause Analysis
-------------------------------------

Analyze the root causes of anomalies using ``CausalRootCauseAnalyzer``:

.. code-block:: python

   from src.prorca.pathway import CausalRootCauseAnalyzer

   analyzer = CausalRootCauseAnalyzer(scm, min_score_threshold=0.8)
   results = analyzer.analyze(df_anomalous, anomaly_dates, start_node='PROFIT_MARGIN')

6. Visualize Causal Pathways
----------------------------

Visualize the discovered causal pathways using ``CausalResultsVisualizer``:

.. code-block:: python

   from src.prorca.pathway import CausalResultsVisualizer

   visualizer = CausalResultsVisualizer(analysis_results=results)
   visualizer.plot_root_cause_paths()