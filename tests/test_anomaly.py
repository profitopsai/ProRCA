import pandas as pd
from anomaly.adtk import AnomalyDetector


def test_anomaly_detector():
    # Create a simple DataFrame for testing
    data = {
        "ORDERDATE": pd.date_range(
            start="2023-01-01", end="2023-01-05", freq="D"
        ),
        "PROFIT_MARGIN": [50, 52, 48, 75, 51],  # Anomaly on 2023-01-04
    }
    df = pd.DataFrame(data)

    # Initialize the detector
    detector = AnomalyDetector(
        df, date_col="ORDERDATE", value_col="PROFIT_MARGIN"
    )

    # Detect anomalies
    anomalies = detector.detect()

    # Check if the anomaly on 2023-01-04 is detected
    assert (
        pd.Timestamp("2023-01-04") in anomalies.index
    ), "Anomaly on 2023-01-04 not detected"
