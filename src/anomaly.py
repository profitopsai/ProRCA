import pandas as pd
import matplotlib.pyplot as plt
from adtk.detector import InterQuartileRangeAD

class AnomalyDetector:
    """
    A class for detecting anomalies in time series data using ADTK's InterQuartileRangeAD.
    It also provides a visualization of the detected anomalies.
    
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the time series data.
    date_col : str, default "ORDERDATE"
        The column name containing date/time information. This column will be set as the DataFrame's index.
    value_col : str, default "PROFIT_MARGIN"
        The column on which anomaly detection is performed.
    """
    def __init__(self, df, date_col="ORDERDATE", value_col="PROFIT_MARGIN"):
        # Work on a copy so as not to modify the original DataFrame.
        self.df = df.copy()
        self.date_col = date_col
        self.value_col = value_col
        
        # Ensure the DataFrame index is set to the date column.
        if self.df.index.name != self.date_col:
            self.df.set_index(self.date_col, inplace=True)
            
        self.anomalies = None

    def detect(self):
        """
        Detect anomalies in the specified value column using InterQuartileRangeAD.
        
        Returns
        -------
        anomalies : pd.DataFrame
            A DataFrame that includes:
              - 'is_anamoly': a boolean flag indicating whether an anomaly was detected.
              - 'value': the original value from the input DataFrame.
        """
        # Initialize the ADTK detector.
        detector = InterQuartileRangeAD()
        # Run the detection on the selected column.
        detection_df = self.df[[self.value_col]]
        detected = detector.fit_detect(detection_df)
        
        # Prepare the anomalies DataFrame:
        anomalies = detected.copy()
        # Add the actual values (for plotting purposes)
        anomalies["value"] = detection_df[self.value_col]
        # Rename the detector output column for clarity.
        anomalies.rename(columns={self.value_col: "is_anamoly"}, inplace=True)
        
        self.anomalies = anomalies
        return anomalies

    def get_anomaly_dates(self):
        """
        Retrieve the dates where anomalies were detected.
        
        Returns
        -------
        anomaly_dates : pd.DatetimeIndex
            The dates (from the DataFrame's index) where an anomaly was detected.
        """
        if self.anomalies is None:
            raise ValueError("Anomalies have not been detected yet. Please call detect() first.")
        
        anomaly_dates = self.anomalies[self.anomalies["is_anamoly"] == True].index
        
        return pd.Series(anomaly_dates, name=anomaly_dates.name)

    def visualize(self, figsize=(12, 6), 
                  title="Daily Profit Margin Over Time with Anomalies Highlighted",
                  xlabel="Date", ylabel="Profit Margin Value", ylim=(40, 60)):
        """
        Visualize the time series data with anomalies highlighted.
        
        Parameters
        ----------
        figsize : tuple, default (12, 6)
            Size of the figure.
        title : str, default "Daily Profit Margin Over Time with Anomalies Highlighted"
            Title for the plot.
        xlabel : str, default "Date"
            Label for the x-axis.
        ylabel : str, default "Profit Margin Value"
            Label for the y-axis.
        ylim : tuple, optional, default (40, 60)
            Y-axis limits.
        """
        if self.anomalies is None:
            raise ValueError("Anomalies have not been detected yet. Please call detect() first.")
        
        plt.figure(figsize=figsize)
        
        # Plot the original time series.
        plt.plot(self.anomalies.index, self.anomalies['value'], 
                 label='Profit Margin', color='black')
        
        # Highlight the anomaly points.
        anomaly_points = self.anomalies[self.anomalies["is_anamoly"] == True]
        plt.scatter(anomaly_points.index, anomaly_points["value"], 
                    color='red', label='Anomaly Detected', s=100)
        
        # Set plot labels and grid.
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.4)
        if ylim is not None:
            plt.ylim(ylim)
        
        plt.show()
