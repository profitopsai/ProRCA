Examples
========

This section provides detailed examples to help you understand how to use ProRCA in practice. The examples are based on Jupyter notebooks included in the repository, which you can download and run locally.

Data Generation Example
-----------------------

The `Data_Generation.ipynb` notebook demonstrates how to generate synthetic fashion sales data and inject anomalies. This is a great starting point to understand how ProRCA creates realistic datasets for testing.

**Download the Notebook**

:download:`Data_Generation.ipynb <../../examples/Example_1/Data_Generation.ipynb>`

**Key Steps**

1. **Generate Synthetic Data**

   The notebook uses the ``generate_fashion_data_with_brand`` function to create a dataset:

   .. code-block:: python

      from src.data_generators.synthetic_sales_data import generate_fashion_data_with_brand
      df = generate_fashion_data_with_brand(start_date="2023-01-01", end_date="2023-12-30")

2. **Inject Anomalies**

   Anomalies are injected using a schedule:

   .. code-block:: python

      from src.data_generators.synthetic_sales_data import inject_anomalies_by_date

      anomaly_schedule = {
          '2023-01-10': ('ExcessiveDiscount', 0.5, 'PricingError', 'Apparel'),
          '2023-06-10': ('COGSOverstatement', -0.8, 'SupplierIssue', 'Footwear'),
          '2023-09-10': ('FulfillmentSpike', -3, 'LogisticsIssue', 'Beauty'),
          '2023-12-10': ('ReturnSurge', 10, 'QualityIssue', 'Accessories')
      }

      df_anomalous = inject_anomalies_by_date(df, anomaly_schedule)

3. **Aggregate Data**

   The data is aggregated by date for further analysis:

   .. code-block:: python

      df_final = df_anomalous.groupby([pd.Grouper(key='ORDERDATE', freq='D')]).agg(aggregation_dict).reset_index()
      df_final.to_csv('fashion_data_with_anomalies_aggregated.csv', index=False)

**Sample Output**

Here’s a preview of the generated data (first 5 rows):

- **ORDERNUMBER**: 58740, 44805, 61786, 81153, 84024
- **QUANTITYORDERED**: 1, 1, 1, 1, 2
- **PRICEEACH**: 150.00, 93.93, 58.96, 35.75, 35.13
- **UNIT_COST**: 44.22, 25.08, 17.03, 9.28, 10.31
- **ORDERDATE**: 2023-01-01 (for all rows)
- **SALES**: 150.00, 93.93, 58.96, 35.75, 70.26
- **DISCOUNT**: 12.00, 11.27, 12.74, 0.00, 13.49
- **NET_SALES**: 138.00, 82.66, 46.22, 35.75, 56.77
- **PROFIT**: 71.76, 43.36, 14.38, 18.13, 26.05
- **PROFIT_MARGIN**: 52.00, 52.46, 31.11, 50.71, 45.89

Root Cause Analysis Example
---------------------------

The `RCA.ipynb` notebook (not provided in the repository) would typically show how to perform root cause analysis using the generated data. You can follow the steps in the :doc:`usage` section to perform a similar analysis.

**Steps Overview**

1. Detect anomalies using ``AnomalyDetector``.
2. Build a Structural Causal Model (SCM) with ``ScmBuilder``.
3. Analyze root causes with ``CausalRootCauseAnalyzer``.
4. Visualize the results with ``CausalResultsVisualizer``.

Refer to the :doc:`usage` section for the complete code.