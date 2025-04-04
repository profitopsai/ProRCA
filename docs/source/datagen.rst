Synthetic Data Generation
=========================

ProRCA includes a dedicated module, ``data_generators``, designed to create realistic datasets for testing, demonstration, and validation purposes. While you are encouraged to use ProRCA with your own operational data, the synthetic data generator provides a valuable tool, especially when you need a controlled environment with known ground truth.

Why Use Synthetic Data?
-----------------------

* **Algorithm Validation:** Test ProRCA's anomaly detection and root cause analysis capabilities against datasets where the anomalies and their causes are known beforehand.
* **Demonstration & Learning:** Provide clear examples and tutorials without requiring sensitive real-world data.
* **Benchmarking:** Create standardized datasets to compare different configurations or versions of analysis techniques.
* **Filling Gaps:** Use synthetic data when real data is scarce, incomplete, or unavailable.

Realism and Quality
-------------------

The data generation process within ProRCA has been meticulously crafted to ensure a high degree of realism:

* **Expert Validation:** The underlying model and parameters, particularly for the initial retail generator, have been developed and validated in consultation with industry experts to reflect common operational dynamics.
* **Causal Structure:** The data is generated based on plausible causal relationships between different business metrics (e.g., price affects sales, quantity affects costs), providing a solid foundation for causal analysis.
* **Realistic Distributions:** Variables are often generated using distributions (like Log-Normal or Poisson) that mimic real-world patterns, rather than simple uniform randomness.
* **Configurability:** Key parameters like date ranges, product details, and pricing strategies can be adjusted.

Current Capabilities: Retail Data
---------------------------------

The first release of ProRCA includes a generator specifically focused on **fashion retail transactions**.

Generate Retail Data
^^^^^^^^^^^^^^^^^^^^

* **Function:** ``generate_fashion_data_with_brand``
* **Purpose:** Creates a realistic DataFrame mimicking retail sales, costs, and profit calculations over time, simulating aspects like different brands, product hierarchies, sales channels, promotions, and customer loyalty.
* **Module:** ``data_generators.synthetic_sales_data``
* **Arguments:**
    * ``start_date`` (str): The beginning date for the data generation period (e.g., "YYYY-MM-DD").
    * ``end_date`` (str): The end date for the data generation period (e.g., "YYYY-MM-DD").
* **Returns:** A ``pandas.DataFrame`` containing the synthetic transaction data. Columns include operational metrics like ``ORDERDATE``, ``QUANTITYORDERED``, ``PRICEEACH``, ``UNIT_COST``, ``SALES``, ``DISCOUNT``, ``NET_SALES``, ``FULFILLMENT_COST``, ``MARKETING_COST``, ``RETURN_COST``, ``COST_OF_GOODS_SOLD``, ``SHIPPING_REVENUE``, ``PROFIT``, ``PROFIT_MARGIN``, as well as contextual dimensions like ``BRAND``, ``MERCHANDISE_HIERARCHY``, ``SALES_CHANNEL``, etc.

.. code-block:: python

   from data_generators.synthetic_sales_data import generate_fashion_data_with_brand

   # Generate synthetic retail data for the year 2023
   df_synthetic = generate_fashion_data_with_brand(start_date="2023-01-01", end_date="2023-12-31")

   print("Generated DataFrame sample:")
   print(df_synthetic.head())

Injecting Controlled Anomalies
------------------------------

A key feature for testing is the ability to inject specific, known anomalies into the dataset. This allows you to verify if ProRCA correctly identifies the root causes you intentionally introduced.

* **Function:** ``inject_anomalies_by_date``
* **Purpose:** Modifies specific metrics on given dates according to a predefined schedule. Crucially, after modifying the source metric (e.g., ``DISCOUNT`` or ``UNIT_COST``), it **recalculates all causally dependent downstream metrics** (like ``NET_SALES``, ``PROFIT``, ``PROFIT_MARGIN``) based on the system's defined logic. This ensures that the *effect* of the injected anomaly propagates realistically through the causal chain, providing a valid test case for root cause analysis.
* **Module:** ``data_generators.synthetic_sales_data``
* **Arguments:**
    * ``df`` (pd.DataFrame): The input DataFrame (can be synthetic or your own data if you want to simulate 'what-if' scenarios).
    * ``anomaly_schedule`` (dict): A dictionary defining the anomalies to inject.
        * *Keys:* Date strings ('YYYY-MM-DD') specifying when the anomaly occurs.
        * *Values:* A tuple containing four elements:
            1. ``anomaly_type`` (str): Defines which metric is directly impacted (e.g., 'ExcessiveDiscount', 'COGSOverstatement', 'FulfillmentSpike', 'ReturnSurge').
            2. ``severity`` (float): A factor controlling the magnitude and direction of the change. The interpretation depends on the `anomaly_type`. For example, a severity of 0.5 for 'ExcessiveDiscount' means the discount is increased by 50% of sales; a severity of 3.0 for 'FulfillmentSpike' means the cost triples (original * (1+3)).
            3. ``root_cause`` (str): A user-defined label for the simulated underlying reason (e.g., 'PricingError', 'SupplierIssue'). This is added to the output DataFrame for validation purposes.
            4. ``scope`` (str): Specifies the segment affected by the anomaly (e.g., a specific product category like 'Apparel', 'Footwear', or a sales channel).
* **Returns:** A new ``pandas.DataFrame`` containing the original data modified by the injected anomalies. It includes additional columns: ``ANOMALY_TYPE``, ``SEVERITY``, and ``ROOT_CAUSE``, marking the rows where anomalies were injected.

.. code-block:: python

   from data_generators.synthetic_sales_data import inject_anomalies_by_date

   # Assume df_synthetic is the DataFrame generated in the previous step

   # Define a schedule of specific anomalies
   anomaly_schedule = {
       '2023-01-10': ('ExcessiveDiscount', 0.5, 'PricingError', 'Apparel'), # 50% discount rate for Apparel
       '2023-06-10': ('COGSOverstatement', -0.8, 'SupplierIssue', 'Footwear'), # Simulates 80% higher unit cost impact for Footwear
       '2023-09-10': ('FulfillmentSpike', 3.0, 'LogisticsIssue', 'Beauty'), # Fulfillment cost quadruples for Beauty
       '2023-12-10': ('ReturnSurge', 10.0, 'QualityIssue', 'Accessories') # Return cost increases 10x for Accessories
   }

   # Inject these anomalies into the synthetic data
   df_anomalous = inject_anomalies_by_date(df_synthetic, anomaly_schedule)

   print("\nDataFrame sample after injecting anomalies:")
   # Notice the new columns ANOMALY_TYPE, SEVERITY, ROOT_CAUSE might be None for non-anomalous rows/dates
   print(df_anomalous[df_anomalous['ORDERDATE'] == '2023-01-10'].head())


Future Directions
-----------------

We plan to significantly expand the ``data_generators`` module in future releases. Our roadmap includes adding synthetic data generators for various other sectors, potentially including:

* Manufacturing (e.g., sensor data, production line metrics)
* Finance (e.g., transaction data, market indicators)
* IT Operations (e.g., server logs, application performance metrics)
* Supply Chain & Logistics

This will broaden the applicability of ProRCA and provide tailored testing environments for diverse use cases.