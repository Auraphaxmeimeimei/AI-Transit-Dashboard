#NYC Transit Intelligence Dashboard

A real-time NYC transit dashboard built with **Python + Dash**, featuring live DOT traffic cameras, AI traffic simulation, ETA & delay prediction, NYC news feed, weather, route maps and dynamic MTA career ads.

> **You can launch this project locally by installing dependencies and running `python app.py` (Option A), or deploy the same repository directly to Hugging Face Spaces using Dash with `app.run_server(host="0.0.0.0", port=7860)` as entrypoint (Option B).**

---

##Features

| Module | Description |
|---|---|
| Live Traffic Cameras | Real-time NYC DOT video feeds |
| AI Detection Simulation | Generates vehicle metrics.csv |
| Auto-updating Traffic Graph | Visualization of cars/buses/trucks |
| ETA Estimation | Predict bus arrival time |
| Delay Prediction | Shows expected traffic delay |
| Route Alternatives | Suggests better bus/subway choices |
| Weather Integration | Queens 10-min refresh |
| NYC RSS News Feed | Latest NYTimes regional news |
| Ads Rotator | Live MTA career suggestions |

---

##Installation & Local Run (Option A)

```bash
git clone https://github.com/Auraphaxmeimeimei/AI-Transit-Dashboard.git
cd AI-Transit-Dashboard
pip install -r requirements.txt
python app.py
Then open:
http://127.0.0.1:7860
Enter the dashboard via the “Enter Dashboard” button.

🚀 Deploy on Hugging Face Spaces (Option B)
Place in repository root:

app.py
requirements.txt
assets/  # route maps

Ensure the end of the app file contains:

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=7860, debug=False)
Create space → choose Dash → upload repo → build → enjoy public link.

Project Structure

AI-Transit-Dashboard/
│── app.py                 # Main dashboard
│── requirements.txt
│── assets/                # PNG bus maps
│── metrics.csv (generated after detection)
└── README.md

Usage Guide
Run detection → metrics.csv generates automatically

Graph updates every 5 sec

ETA/Delay/Recommendation panels activate after detection

Weather/News refresh on schedule

Route selector loads matching PNG maps

Roadmap
Real YOLO object detection integration

Real GTFS Live Bus Feed

Multi-camera view grid

NYC congestion heatmap

Long-term prediction model
