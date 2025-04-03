Welcome to ProRCA's Documentation!
==================================

.. image:: https://i.postimg.cc/L87fQdGG/Final-Logo.jpg
   :alt: ProRCA Logo
   :align: center

**ProRCA** is an end-to-end framework for diagnosing anomalies in complex operational environments by uncovering multi-hop causal pathways. Unlike traditional anomaly detection methods that focus on correlations or feature importance (e.g., via SHAP), our approach leverages structural causal modeling to trace the full causal chain—from hidden root causes to observed anomalies.

Inspired by the paper:

   **Beyond Traditional Problem-Solving: A Causal Pathway Approach for Complex Operational Environments**  
   *Ahmed Dawoud & Shravan Talupula, February 9, 2025* `[📄 Download PDF] <https://arxiv.org/abs/2503.01475>`_

This work introduces a methodology that combines conditional anomaly scoring with causal path discovery and ranking. By extending the `DoWhy <https://github.com/py-why/dowhy>`_ library, the framework provides decision-makers with actionable insights into the true source of complex operational disruptions.

Key Capabilities
----------------

ProRCA empowers you to move from simply detecting anomalies to truly understanding their origins. Here’s how:

-   **Pinpoint Critical Anomalies:** Don't just find outliers; identify the significant operational hiccups in your time series data that truly matter. ProRCA uses robust detection methods to flag the starting points for your investigation.

-   **Map Your System's Causal DNA:** Go beyond black boxes. Explicitly define and model the cause-and-effect relationships within your operations using Structural Causal Models (SCMs). This captures the real logic of how different parts of your system influence each other.

-   **Uncover the *Real* Root Causes:** This is where ProRCA shines. Move past simple correlations and discover the *actual* causal pathways leading to anomalies. Our analysis traces disruptions back through multiple steps (multi-hop paths) in your system, uniquely combining structural knowledge with noise pattern analysis to pinpoint the true origins.

-   **Visualize Causal Stories:** Complex findings become clear insights. ProRCA generates intuitive diagrams of the discovered causal pathways, making it easy to see the chain of events, understand the flow of influence, and communicate exactly where the problem started.


Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   examples
   contributing
   changelog