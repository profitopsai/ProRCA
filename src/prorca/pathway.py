# pathway.py
import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple

import dowhy.gcm as gcm
from dowhy.gcm.anomaly_scorers import MedianCDFQuantileScorer
from dowhy.gcm import anomaly, attribute_anomalies

from graphviz import Digraph
from IPython.display import Image, display


class ScmBuilder:
    """
    A builder class to construct a Structural Causal Model (SCM) from a given set of edges
    (and optionally nodes). It also provides a visualization of the causal graph if desired.

    Parameters
    ----------
    edges : list of tuple
        List of edges in the format (source, target) representing causal relationships.
    nodes : list of str, optional
        List of nodes to include in the graph. If not provided, nodes are automatically inferred from edges.
    visualize : bool, default False
        Whether to visualize the constructed causal graph using Graphviz.
    viz_filename : str, default "dag_relationships"
        The base filename (without extension) to use for saving the graph visualization.
    random_seed : int, default 0
        Random seed for reproducibility when building and fitting the SCM.
    """

    def __init__(
        self,
        edges,
        nodes=None,
        visualize=False,
        viz_filename="dag_relationships",
        random_seed=0,
    ):
        self.edges = edges
        self.nodes = nodes
        self.visualize = visualize
        self.viz_filename = viz_filename
        self.random_seed = random_seed

        self.causal_graph = None
        self.scm = None

    def build_graph(self):
        """
        Build a networkx directed graph (DiGraph) from the provided nodes and edges.

        Returns
        -------
        causal_graph : nx.DiGraph
            The constructed causal graph.
        """
        self.causal_graph = nx.DiGraph()

        # If a list of nodes is provided, add them explicitly
        if self.nodes:
            self.causal_graph.add_nodes_from(self.nodes)

        # Add edges (this will automatically add any nodes that are not already in the graph)
        self.causal_graph.add_edges_from(self.edges)
        return self.causal_graph

    def visualize_graph(self):
        """
        Visualize the causal graph using Graphviz.

        Returns
        -------
        image : IPython.display.Image
            The rendered image of the graph (useful in notebook environments).

        Raises
        ------
        ValueError
            If the causal graph has not yet been built.
        """
        if self.causal_graph is None:
            raise ValueError("Causal graph not built. Please call build_graph() first.")

        dag = Digraph(format="png", engine="dot")
        # Add each edge to the Graphviz graph
        for source, target in self.edges:
            dag.edge(source, target)

        # Render and save the graph image; view=True will open it in a default viewer
        dag.render(self.viz_filename, view=True)
        # Return the image object for inline display in notebooks
        return Image(f"{self.viz_filename}.png")

    def build_scm(self, df=None):
        """
        Build the Structural Causal Model (SCM) from the causal graph.
        If a DataFrame is provided, the method will automatically assign causal mechanisms
        and fit the model.

        Parameters
        ----------
        df : pd.DataFrame, optional
            The data to use for automatically assigning generative models to each node and fitting the SCM.

        Returns
        -------
        scm : gcm.StructuralCausalModel
            The constructed (and possibly fitted) SCM.
        """
        # Set the random seed for reproducibility
        gcm.util.general.set_random_seed(self.random_seed)

        if self.causal_graph is None:
            self.build_graph()

        # Create the SCM from the causal graph
        self.scm = gcm.StructuralCausalModel(self.causal_graph)

        # If a DataFrame is provided, perform auto-assignment and fit the model
        if df is not None:
            print("Automatically assigning causal mechanisms...")
            auto_assignment_summary = gcm.auto.assign_causal_mechanisms(
                self.scm, df, gcm.auto.AssignmentQuality.BETTER
            )
            print("Fitting the Structural Causal Model...")
            gcm.fit(self.scm, df)
            print(auto_assignment_summary)

        return self.scm

    def build(self, df=None):
        """
        Convenience method to build the causal graph, optionally visualize it,
        and then construct the SCM (with optional auto-assignment and fitting if data is provided).

        Parameters
        ----------
        df : pd.DataFrame, optional
            The data to use for automatically assigning causal mechanisms and fitting the SCM.

        Returns
        -------
        scm : gcm.StructuralCausalModel
            The final Structural Causal Model.
        """
        self.build_graph()
        if self.visualize:
            self.visualize_graph()
        return self.build_scm(df)


class CausalRootCauseAnalyzer:
    """
    Advanced root cause analyzer combining structural and noise-based approaches.
    """

    def __init__(self, scm, min_score_threshold: float = 0.8):
        self.scm = scm
        self.min_score_threshold = min_score_threshold
        self.noise_contributions = None
        self.node_scores = None

    def _calculate_noise_contributions(
        self, df_agg: pd.DataFrame, anomaly_dates
    ) -> Dict[str, np.ndarray]:
        """
        Calculate noise-based contributions for each node using DoWhy's attribution.
        """
        noise_contributions = {}
        anomaly_samples = df_agg[df_agg["ORDERDATE"].isin(anomaly_dates)]

        for node in self.scm.graph.nodes():
            try:
                # Use DoWhy's attribute_anomalies for each node
                contributions = attribute_anomalies(
                    causal_model=self.scm,
                    target_node=node,
                    anomaly_samples=anomaly_samples,
                    anomaly_scorer=MedianCDFQuantileScorer(),
                    attribute_mean_deviation=True,
                    num_distribution_samples=5000,
                )
                # Ensure contributions is a numpy array
                if isinstance(contributions, dict):
                    # If it's a dictionary, extract the values we need
                    # This might need adjustment based on the actual structure
                    contributions = np.array(list(contributions.values()))
                noise_contributions[node] = contributions
            except Exception as e:
                print(
                    f"Warning: Could not calculate noise contribution for {node}: {e}"
                )
                noise_contributions[node] = np.array([0.0])  # Default value
                continue

        return noise_contributions

    def _calculate_structural_scores(
        self, df_agg: pd.DataFrame, anomaly_dates
    ) -> Dict[str, np.ndarray]:
        """
        Calculate structural anomaly scores using conditional mechanisms.
        """
        node_scores = {}

        for node in self.scm.graph.nodes():
            mechanism = self.scm.causal_mechanism(node)
            parents = list(self.scm.graph.predecessors(node))

            if mechanism and parents:
                parent_samples = df_agg[parents].values
                target_samples = df_agg[node].values

                scores = anomaly.conditional_anomaly_scores(
                    parent_samples=parent_samples,
                    target_samples=target_samples,
                    causal_mechanism=mechanism,
                    num_samples_conditional=10000,
                )

                node_scores[node] = scores[df_agg["ORDERDATE"].isin(anomaly_dates)]

        return node_scores

    def _calculate_combined_score(self, node: str) -> float:
        """
        Enhanced combined score calculation with better weighting.
        """
        if node not in self.node_scores or node not in self.noise_contributions:
            return 0.0

        try:
            structural_score = float(self.node_scores[node].mean())

            # Get the maximum absolute noise contribution
            noise_contribution = self.noise_contributions[node]
            if not isinstance(noise_contribution, np.ndarray):
                noise_contribution = np.array(noise_contribution)
            noise_score = float(np.max(np.abs(noise_contribution)))

            # Weighted combination favoring structural scores
            if structural_score + noise_score == 0:
                return 0.0

            combined_score = 0.7 * structural_score + 0.3 * noise_score
            return combined_score

        except Exception as e:
            print(f"Warning: Error calculating combined score for {node}: {e}")
            return 0.0

    def _find_root_cause_paths(self, start_node: str) -> List[List[Tuple[str, float]]]:
        """
        Find paths to root causes using combined scoring approach with improved criteria.
        """
        all_paths = []
        visited = set()
        stack = [
            (
                start_node,
                [(start_node, self._calculate_combined_score(start_node))],
            )
        ]

        while stack:
            current_node, current_path = stack.pop()
            parents = list(self.scm.graph.predecessors(current_node))

            # If no parents, consider this a potential root cause
            if not parents:
                if current_path[-1][1] >= self.min_score_threshold:
                    all_paths.append(current_path)
                continue

            # Track if we found any significant parent
            found_significant_parent = False

            for parent in parents:
                if parent in visited:
                    continue

                parent_score = self._calculate_combined_score(parent)

                # More lenient threshold for intermediate nodes
                if parent_score >= self.min_score_threshold * 0.7:
                    found_significant_parent = True
                    new_path = current_path + [(parent, parent_score)]
                    stack.append((parent, new_path))
                    visited.add(parent)

            # If no significant parents found, consider this a root cause
            if (
                not found_significant_parent
                and current_path[-1][1] >= self.min_score_threshold
            ):
                all_paths.append(current_path)

        return all_paths

    def analyze(
        self,
        df_agg: pd.DataFrame,
        anomaly_dates,
        start_node: str = "PROFIT_MARGIN",
    ) -> Dict:
        """
        Main analysis method combining all approaches.
        """
        print("Calculating noise-based contributions...")
        self.noise_contributions = self._calculate_noise_contributions(
            df_agg, anomaly_dates
        )

        print("Calculating structural anomaly scores...")
        self.node_scores = self._calculate_structural_scores(df_agg, anomaly_dates)

        print("\nIdentifying root cause paths...")
        paths = self._find_root_cause_paths(start_node)

        # Calculate path significance using combined metrics
        path_scores = []
        for path in paths:
            root_node = path[-1][0]
            path_score = self._calculate_path_significance(path, root_node)
            path_scores.append((path, path_score))

        # Sort by significance
        sorted_paths = sorted(path_scores, key=lambda x: x[1], reverse=True)

        self._print_analysis_results(sorted_paths)

        return {
            "paths": sorted_paths,
            "node_scores": self.node_scores,
            "noise_contributions": self.noise_contributions,
        }

    def analyze_by_date(
        self,
        df_agg: pd.DataFrame,
        anomaly_dates,
        start_node: str = "PROFIT_MARGIN",
    ) -> Dict:
        """
        Run the analysis separately for each anomaly date so that date-specific root causes are captured.

        Parameters
        ----------
        df_agg : pd.DataFrame
            The aggregated data containing an 'ORDERDATE' column.
        anomaly_dates : iterable
            An iterable of anomaly dates (e.g., a list or DatetimeIndex).
        start_node : str, default 'PROFIT_MARGIN'
            The starting node for the root cause analysis.

        Returns
        -------
        results : dict
            A dictionary where each key is an anomaly date and the value is the analysis result for that date.
        """
        results = {}
        for ad in anomaly_dates:
            print(f"\n--- Analyzing anomaly date: {ad} ---")
            # Filter for a single anomaly date (wrap the date in a list so that .isin works)
            current_date = [ad]
            self.noise_contributions = self._calculate_noise_contributions(
                df_agg, current_date
            )
            self.node_scores = self._calculate_structural_scores(df_agg, current_date)
            paths = self._find_root_cause_paths(start_node)
            path_scores = []
            for path in paths:
                root_node = path[-1][0]
                path_score = self._calculate_path_significance(path, root_node)
                path_scores.append((path, path_score))
            sorted_paths = sorted(path_scores, key=lambda x: x[1], reverse=True)
            results[ad] = {
                "paths": sorted_paths,
                "node_scores": self.node_scores,
                "noise_contributions": self.noise_contributions,
            }
            self._print_analysis_results(sorted_paths)
        return results

    def _calculate_path_significance(
        self, path: List[Tuple[str, float]], root_node: str
    ) -> float:
        """
        Calculate path significance using causal consistency metrics.
        """
        # Get noise contribution of root node
        root_noise = np.mean(self.noise_contributions.get(root_node, [0]))

        # Calculate path consistency
        path_nodes = [node for node, _ in path]
        consistency_score = self._evaluate_causal_consistency(path_nodes)

        # Fallback to 0 if consistency_score is NaN
        if np.isnan(consistency_score):
            consistency_score = 0.0

        # Combine scores with theoretical weights
        return 0.7 * root_noise + 0.3 * consistency_score

    def _evaluate_causal_consistency(self, path_nodes: List[str]) -> float:
        """
        Evaluate causal consistency of the path using noise patterns.
        """
        consistency_scores = []
        for i in range(len(path_nodes) - 1):
            current = path_nodes[i]
            next_node = path_nodes[i + 1]

            curr_array = self.noise_contributions.get(current, [0])
            next_array = self.noise_contributions.get(next_node, [0])

            # If there are not enough data points, skip the correlation calculation.
            if len(curr_array) < 2 or len(next_array) < 2:
                continue

            correlation_matrix = np.corrcoef(curr_array, next_array)
            correlation = correlation_matrix[0, 1]

            # Replace NaN correlations with 0
            if np.isnan(correlation):
                correlation = 0.0
            consistency_scores.append(abs(correlation))

        return np.mean(consistency_scores) if consistency_scores else 0.0

    def _print_analysis_results(
        self, sorted_paths: List[Tuple[List[Tuple[str, float]], float]]
    ):
        """
        Print detailed analysis results.
        """
        print(f"\nFound {len(sorted_paths)} potential root cause paths.")
        print("\nDetailed path analysis (ordered by causal significance):")
        print("-" * 60)

        for i, (path, significance) in enumerate(sorted_paths, 1):
            print(f"\nPath {i} (Causal Significance: {significance:.4f}):")
            for j, (node, score) in enumerate(path):
                prefix = "└─" if j == len(path) - 1 else "├─"
                noise_contrib = np.mean(self.noise_contributions.get(node, [0]))
                print(
                    f"{'  ' * j}{prefix} {node:<20} "
                    f"(Combined Score: {score:.4f}, Noise Contribution: {noise_contrib:.4f})"
                )


class CausalResultsVisualizer:
    """
    Visualizes the results from CausalRootCauseAnalyzer. The class expects the analysis results to contain:
      - 'paths': a list of tuples (path, significance), where each path is a list of tuples (node, combined_score)
      - 'node_scores': a dict mapping node -> array of structural scores
      - 'noise_contributions': a dict mapping node -> array of noise contributions

    It offers several plotting methods:
      - plot_root_cause_paths: a network diagram of the root cause pathways.
      - plot_node_scores: a bar chart of average structural scores per node.
      - plot_noise_contributions_distribution: a boxplot for the distribution of noise contributions.
      - plot_consistency_heatmap: a heatmap of the correlation between nodes' noise contributions.
      - plot_timeline: a timeline plot if you run separate analyses per anomaly date.
    """

    def __init__(self, analysis_results):
        """
        Parameters
        ----------
        analysis_results : dict
            Results from the analyzer.analyze() call. Expected keys are 'paths', 'node_scores', and 'noise_contributions'.
        """
        self.results = analysis_results

    def plot_root_cause_paths(self):
        """
        Visualize the discovered root cause pathways using Graphviz for clarity.
        Each path is displayed as a separate cluster with a background color in a gradient
        that starts from light green and moves to yellow. The order of nodes is reversed such that
        the root cause appears first and the final outcome (e.g., 'PROFIT_MARGIN') appears last.
        Duplicate arrows for identical edges across different paths are omitted.
        The chart is rendered inline in a Jupyter Notebook.
        """
        paths = self.results.get("paths", [])
        if not paths:
            print("No root cause paths found.")
            return

        total_paths = len(paths)

        # Helper function to interpolate between two hex colors.
        def interpolate_color(color1, color2, factor):
            # Remove the '#' and convert to integers.
            r1, g1, b1 = (
                int(color1[1:3], 16),
                int(color1[3:5], 16),
                int(color1[5:7], 16),
            )
            r2, g2, b2 = (
                int(color2[1:3], 16),
                int(color2[3:5], 16),
                int(color2[5:7], 16),
            )
            r = int(r1 + factor * (r2 - r1))
            g = int(g1 + factor * (g2 - g1))
            b = int(b1 + factor * (b2 - b1))
            return f"#{r:02x}{g:02x}{b:02x}"

        # Define the gradient endpoints:
        # Start with light green and end with yellow.
        color_start = "#50C878"  # Light green.
        color_end = "#ffff99"  # Yellow.

        # Create the main Graphviz digraph.
        dot = Digraph(format="png")

        # Global set to track already added edges (to avoid duplicates).
        added_edges = set()

        # Iterate over each discovered path.
        for idx, (path, significance) in enumerate(paths):
            # Compute a gradient factor: 0 for the first path, 1 for the final path.
            factor = idx / (total_paths - 1) if total_paths > 1 else 0
            fill_color = interpolate_color(color_start, color_end, factor)

            # Reverse the path so that arrows point from the root cause to the final outcome.
            reversed_path = path[::-1]
            with dot.subgraph(name=f"cluster_{idx}") as c:
                # Set the cluster background to the computed gradient color.
                c.attr(style="filled", fillcolor=fill_color)
                c.attr(label=f"Path {idx+1}\nSignificance: {significance:.2f}")
                for i, (node, combined_score) in enumerate(reversed_path):
                    node_label = f"{node}\n({combined_score:.2f})"
                    # Add the node using its name as a unique identifier.
                    c.node(
                        node,
                        label=node_label,
                        shape="box",
                        style="rounded,filled",
                        fillcolor="skyblue",
                    )
                    # Add an edge to the next node if available.
                    if i < len(reversed_path) - 1:
                        next_node = reversed_path[i + 1][0]
                        edge_tuple = (node, next_node)
                        if edge_tuple not in added_edges:
                            c.edge(node, next_node, arrowhead="normal")
                            added_edges.add(edge_tuple)

        # Render the Graphviz diagram to a PNG image and display it inline.
        png_data = dot.pipe(format="png")
        display(Image(png_data))
