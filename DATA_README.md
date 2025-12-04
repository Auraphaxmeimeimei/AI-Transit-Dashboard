## Dataset Documentation

This project currently uses a simulated dataset created programmatically to support dashboard visualization and predictive modules.

### Generated File

| File | Source | Description |
|---|---|---|
| metrics.csv | Generated via run_detection_for_dashboard() | Contains time-series vehicle counts for cars, buses, trucks |

metrics.csv is created when the user clicks "Run AI Detection".
No dataset is required beforehand to run the dashboard.

### Data Flow

1. Detection trigger produces a list of timestamped vehicle counts.
2. The records are stored locally as metrics.csv.
3. Dashboard reads this file every refresh interval for plotting and calculations.

### Data Usage

| Component | Uses metrics.csv? |
|---|---|
| Traffic Graph | Yes |
| ETA Estimation | Yes |
| Delay Prediction | Yes |
| Alternative Route Advice | Yes |
| Weather + News Panels | No |
| Route Map Viewer | No |

### Data Expansion Plan

| Future Dataset | Potential Integration |
|---|---|
| Live YOLO detection output | Replace simulation values with actual counts |
| GTFS feed | Real-time bus tracking and ETA inference |
| Traffic speed sensors if available | Congestion scoring improvement |
| Historical CSV logs | Long-term performance analytics |
