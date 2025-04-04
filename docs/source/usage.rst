Usage Guide
===========

This guide walks you through the typical workflow for using ProRCA, from preparing your data to visualizing the identified causal root causes of anomalies.

**Core Workflow:**

1.  **Prepare Data:** Load your operational time series data.
2.  **Detect Anomalies:** Identify significant deviations in a key metric.
3.  **Define Causal Structure:** Specify the known cause-and-effect relationships in your system (the DAG).
4.  **Build Structural Causal Model (SCM):** Create and fit a model representing your system's causal dynamics.
5.  **Perform Causal Root Cause Analysis:** Trace the detected anomalies back through the SCM to find their origins.
6.  **Visualize Results:** Understand the findings through intuitive diagrams.

Let's dive into each step.

Step 1: Prepare Your Data (Real or Synthetic)
---------------------------------------------

ProRCA works with your own operational data. The primary requirement is that your data is in a :code:`pandas.DataFrame` format and contains:

* A time-based column (ideally datetime objects) that can be set as the index.
* Numerical columns representing the metrics involved in your system (e.g., sales, costs, profit margin).

Simply load your data using pandas or your preferred method. For example:

.. code-block:: python

   import pandas as pd

   # Example: Load data from a CSV file
   # Ensure 'YourDateColumn' is parsed as datetime
   my_data = pd.read_csv('path/to/your/data.csv', parse_dates=['YourDateColumn'])

   # It's often helpful to set the date column as the index
   my_data = my_data.set_index('YourDateColumn')

   # --- Proceed to Step 2: Detect Anomalies ---

Step 2: Detect Anomalies
------------------------

Now, identify anomalies in a key performance indicator (KPI) using ProRCA's detector, which wraps the ADTK library.

* **Class:** :code:`AnomalyDetector`
* **Purpose:** Detects anomalies in a specified time series column using the Interquartile Range (IQR) method. In next releases we will support more methods.
* **Module:** :code:`anomaly.adtk`
* **Initialization Arguments (:code:`__init__`):**
   * :code:`df` (pd.DataFrame): The input data (e.g., :code:`data_to_analyze`).
   * :code:`date_col` (str): The name of the column containing datetime information (must match your data). Defaults to "ORDERDATE".
   * :code:`value_col` (str): The name of the numerical column where you want to detect anomalies (your KPI). Defaults to "PROFIT_MARGIN".
* **Methods:**
   * :code:`detect()`: Runs the IQR anomaly detection algorithm. **Returns:** A :code:`pd.DataFrame` with the same index as the input, containing a boolean column named :code:`'is_anamoly'` (True if an anomaly is detected) and a :code:`'value'` column with the original KPI values.
   * :code:`get_anomaly_dates()`: Extracts the dates/timestamps where anomalies were detected. **Returns:** A :code:`pd.Series` or :code:`pd.DatetimeIndex` containing only the timestamps corresponding to detected anomalies.
   * :code:`visualize()`: Plots the time series (:code:`value_col`) and highlights the detected anomalies. **Arguments:** Standard matplotlib arguments like :code:`figsize` (tuple), :code:`ylim` (tuple), :code:`title` (str), etc. **Returns:** None (displays the plot).

.. code-block:: python

   from anomaly.adtk import AnomalyDetector

   # Initialize the detector on our data, looking at 'PROFIT_MARGIN'
   # Ensure 'date_col' matches your DataFrame's date column name
   detector = AnomalyDetector(data_to_analyze, date_col="ORDERDATE", value_col="PROFIT_MARGIN")

   # Run the detection
   anomaly_results_df = detector.detect()

   # Get the specific dates where anomalies occurred
   anomaly_dates = detector.get_anomaly_dates()
   print(f"\nDetected anomaly dates:\n{anomaly_dates}")

   # Visualize the profit margin time series with anomalies marked
   print("\nVisualizing anomalies...")
   detector.visualize(figsize=(14, 7), ylim=(0, 70), title="Profit Margin Anomalies")


Step 3: Define Causal Structure (DAG)
-------------------------------------

This is a critical step where you define the cause-and-effect relationships within your system as a Directed Acyclic Graph (DAG). An accurate DAG, based on your domain knowledge, is essential for meaningful causal analysis.
ProRCA currently does not support causal discovery tasks, but we plan to add this feature in future releases.

Define the causal links explicitly as a list of tuples, where each tuple `(source, target)` means `source` causes `target`.

* **Purpose:** To encode your specific understanding of how variables influence each other.
* **Format:** List of `(str, str)` tuples.
* **Requirement:** Must be acyclic (no circular dependencies).

.. code-block:: python

   # Define the causal relationships based on domain knowledge
   # Example based on the synthetic data's logic:
   manual_edges = [
       ("PRICEEACH", "UNIT_COST"), ("PRICEEACH", "SALES"),
       ("UNIT_COST", "COST_OF_GOODS_SOLD"),
       ("QUANTITYORDERED", "SALES"), ("QUANTITYORDERED", "COST_OF_GOODS_SOLD"),
       ("QUANTITYORDERED", "FULFILLMENT_COST"), # Added based on generator logic
       ("SALES", "DISCOUNT"), ("SALES", "NET_SALES"),
       ("DISCOUNT", "NET_SALES"),
       ("NET_SALES", "FULFILLMENT_COST"), # Consider if NET_SALES influences costs
       ("NET_SALES", "MARKETING_COST"),   # Or if costs are independent drivers
       ("NET_SALES", "RETURN_COST"),
       ("NET_SALES", "PROFIT"),
       ("FULFILLMENT_COST", "PROFIT"),
       ("MARKETING_COST", "PROFIT"),
       ("RETURN_COST", "PROFIT"),
       ("COST_OF_GOODS_SOLD", "PROFIT"),
       ("SHIPPING_REVENUE", "PROFIT"), # Assuming shipping revenue adds to profit
       ("PROFIT", "PROFIT_MARGIN"),
       ("NET_SALES", "PROFIT_MARGIN") # Profit margin is Profit / Net Sales
   ]

   # Assign the chosen edges for the next step
   causal_edges = manual_edges


Step 4: Build the Structural Causal Model (SCM)
-----------------------------------------------

With the DAG defined, create and fit a Structural Causal Model using DoWhy's GCM framework.

* **Class:** :code:`ScmBuilder`
* **Purpose:** Takes the causal graph structure (edges) and data to build and fit an SCM instance. It automatically assigns appropriate causal mechanisms (e.g., regression models, classifiers) to each node based on its parents and data type.
* **Module:** :code:`prorca.pathway`
* **Initialization Arguments (:code:`__init__`):**
   * :code:`edges` (list): The list of edge tuples defined in Step 4 (e.g., :code:`causal_edges`).
   * :code:`nodes` (list, optional): Explicitly list nodes if needed (usually inferred from edges).
   * :code:`visualize` (bool): If True, displays the DAG using Graphviz (requires Graphviz installation). Default: False.
   * :code:`random_seed` (int): Seed for reproducibility in model fitting. Default: 0.
* **Methods:**
   * :code:`build(df)`: Constructs the :code:`nx.DiGraph`, assigns causal mechanisms based on the provided data, and fits the SCM.
      * **Arguments:** :code:`df` (pd.DataFrame): The data used to learn the relationships (e.g., :code:`data_to_analyze`).
      * **Returns:** A fitted :code:`dowhy.gcm.StructuralCausalModel` object.

.. code-block:: python

   from prorca.pathway import ScmBuilder

   print("\nBuilding Structural Causal Model...")
   # Initialize the builder with the defined edges
   builder = ScmBuilder(edges=causal_edges, visualize=False) # Set visualize=True to see the DAG plot

   # Build and fit the SCM using the data
   scm = builder.build(df=data_to_analyze)

   print("SCM built and fitted.")


Step 5: Perform Causal Root Cause Analysis
------------------------------------------

Now, use the fitted SCM to trace the anomalies back to their potential root causes.

* **Class:** :code:`CausalRootCauseAnalyzer`
* **Purpose:** Implements the core RCA logic, combining structural graph traversal with anomaly scores derived from the SCM's learned mechanisms and noise distributions. It ranks potential causal pathways based on significance.
* **Module:** :code:`prorca.pathway`
* **Initialization Arguments (:code:`__init__`):**
   * :code:`scm` (gcm.StructuralCausalModel): The fitted SCM object from Step 5.
   * :code:`min_score_threshold` (float): A threshold (0 to 1) to filter out paths where the root node's combined anomaly score is too low. Higher values mean stricter filtering. Default: 0.8.
* **Methods:**
   * :code:`analyze(df, anomaly_dates, start_node)`: Performs RCA considering *all* specified anomaly dates together. It calculates average scores across these dates.
      * **Arguments:**
         * :code:`df` (pd.DataFrame): The data used for analysis (e.g., :code:`data_to_analyze`).
         * :code:`anomaly_dates` (list/Series): The specific dates/timestamps of the anomalies detected in Step 3.
         * :code:`start_node` (str): The name of the node where the anomaly was initially observed (your KPI, e.g., "PROFIT_MARGIN").
      * **Returns:** A dictionary containing:
         * :code:`'paths'`: A list of tuples :code:`(path, significance_score)`, sorted by significance. Each :code:`path` is itself a list of tuples :code:`(node_name, combined_score)`.
         * :code:`'node_scores'`: Dictionary mapping node names to their structural anomaly scores for the analyzed dates.
         * :code:`'noise_contributions'`: Dictionary mapping node names to their noise-based anomaly contributions.
   * :code:`analyze_by_date(df, anomaly_dates, start_node)`: **(Alternative)** Performs RCA *separately for each* anomaly date in the list. This is useful for isolating causes specific to individual events.
      * **Arguments:** Same as :code:`analyze`.
      * **Returns:** A dictionary where *keys* are the individual anomaly dates (from :code:`anomaly_dates`) and *values* are the results dictionaries (same format as :code:`analyze` output) specific to that single date.

.. code-block:: python

   from prorca.pathway import CausalRootCauseAnalyzer

   print("\nPerforming Causal Root Cause Analysis...")
   # Initialize the analyzer with the SCM
   analyzer = CausalRootCauseAnalyzer(scm, min_score_threshold=0.7) # Adjust threshold as needed

   # --- Choose ONE analysis method ---

   # Method 1: Analyze all anomalies together
   # print("Analyzing all detected anomalies collectively...")
   # analysis_results = analyzer.analyze(data_to_analyze, anomaly_dates, start_node='PROFIT_MARGIN')

   # Method 2: Analyze each anomaly date separately (RECOMMENDED for distinct events)
   print("Analyzing each anomaly date individually...")
   # Use only the first anomaly date for this example snippet, but typically pass all dates
   analysis_results_by_date = analyzer.analyze_by_date(data_to_analyze, anomaly_dates, start_node='PROFIT_MARGIN')

   # For visualization, we'll pick the results for the first date if using analyze_by_date
   # If using analyze(), just use analysis_results directly
   first_date = anomaly_dates.iloc[0]
   results_to_visualize = analysis_results_by_date[first_date] if isinstance(analysis_results_by_date, dict) else analysis_results # Adjust if needed

   # The analyzer prints detailed path information during execution.


Step 6: Visualize Causal Pathways
---------------------------------

Finally, visualize the discovered root cause paths for easier interpretation.

* **Class:** :code:`CausalResultsVisualizer`
* **Purpose:** Creates plots from the output of the :code:`CausalRootCauseAnalyzer`.
* **Module:** :code:`prorca.pathway`
* **Initialization Arguments (:code:`__init__`):**
   * :code:`analysis_results` (dict): The results dictionary returned by the :code:`analyze()` or one entry from the :code:`analyze_by_date()` output.
* **Methods:**
   * :code:`plot_root_cause_paths()`: Generates and displays a Graphviz diagram showing the most significant causal pathways found. Paths are ranked, and nodes show their combined anomaly scores.
* **Returns:** None (displays the plot inline, typically in a Jupyter environment).

.. code-block:: python

   from prorca.pathway import CausalResultsVisualizer

   print("\nVisualizing the results...")
   # Initialize the visualizer with the results dictionary
   visualizer = CausalResultsVisualizer(analysis_results=results_to_visualize)

   # Plot the ranked root cause paths
   visualizer.plot_root_cause_paths()


   