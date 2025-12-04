import os
import time
import math
import json
from datetime import datetime, timezone
from random import randint

import pandas as pd
import requests
import feedparser
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

# =========================================================
# ROUTE MAP
# =========================================================

ROUTE_MAP = {
    "M15 (Manhattan)": "https://www.transsee.ca/?r=mta:M15",
    "Q32 (Queens)": "https://www.transsee.ca/?r=mta:Q32",
    "B62 (Brooklyn)": "https://www.transsee.ca/?r=mta:B62",
    "Bx12 (Bronx)": "https://www.transsee.ca/?r=mta:Bx12",
}

# =========================================================
# CAMERA_STREAM_GROUPS
# =========================================================

CAMERA_STREAM_GROUPS = {

    # ====================================================
    # I-678 Van Wyck — Served by Q25, Q44-SBS
    # ====================================================
    "I-678 Van Wyck Expressway — Served by Q25": {
        "I-678 at 133rd Avenue Northbound": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_159/playlist.m3u8",
        "I-678 at 133rd Avenue Southbound": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_160/playlist.m3u8",
        "I-678 at College Point Blvd": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_184/playlist.m3u8",
        "I-678 at North Conduit Avenue": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_157/playlist.m3u8",
        "I-678 at South Conduit Avenue": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_158/playlist.m3u8",
        "I-678 at 73rd Terrace": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_181/playlist.m3u8",
        "I-678 at 67th Road": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_182/playlist.m3u8",
        "I-678 at L.I.E.": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_183/playlist.m3u8",
        "I-678 at Avery Avenue": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_185/playlist.m3u8",
        "I-678 at Northern Blvd": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_186/playlist.m3u8",
        "I-678 at 25th Road": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_187/playlist.m3u8",
        "I-678 at 14th Avenue": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_188/playlist.m3u8",
        "I-678 at 82nd Avenue": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_265/playlist.m3u8",
        "I-678 at Jewel Avenue": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_299/playlist.m3u8",
        "I-678 at Foch Blvd Northbound": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_163/playlist.m3u8",
        "I-678 at Foch Blvd Southbound": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_164/playlist.m3u8",
        "I-678 between 115th Ave & 166th Ave": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_165/playlist.m3u8",
        "I-678 at 111th Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_166/playlist.m3u8",
        "I-678 at 109th Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_167/playlist.m3u8",
        "I-678 at 107th Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_168/playlist.m3u8",
        "I-678 at 101st Avenue Northbound": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_169/playlist.m3u8",
        "I-678 at 101st Avenue Southbound": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_170/playlist.m3u8",
        "I-678 at Alwick Road": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_161/playlist.m3u8",
        "I-678 at Rockaway Blvd": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_162/playlist.m3u8",
    },

    # ====================================================
    # I-278 BQE — Queens side → Served by Q18, Q66
    # ====================================================
    "I-278 (BQE) Queens Section — Served by Q18 / Q66": {
        "I-278 at 56th Road": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_222/playlist.m3u8",
        "I-278 at Northern Blvd": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_101/playlist.m3u8",
        "I-278 at 31st Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_102/playlist.m3u8",
        "I-278 at 30th Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_103/playlist.m3u8",
        "I-278 at 49th Street": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_104/playlist.m3u8",
        "I-278 Connector at 31st Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_105/playlist.m3u8",
        "I-278 Connector to GCP / Astoria Blvd": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_106/playlist.m3u8",
    },

    # ====================================================
    # I-295 / Cross Island Pkwy
    # ====================================================
    "I-295 / Cross Island Parkway": {
        "I-295 at Union Turnpike": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_107/playlist.m3u8",
        "I-295 at 64th Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_108/playlist.m3u8",
        "I-295 at 56th Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_109/playlist.m3u8",
        "I-295 at 48th Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_110/playlist.m3u8",
        "295 just south of VMS66": "https://s53.nysdot.skyvdn.com:443/rtplive/R10_176/playlist.m3u8",
        "CIP at Northern Blvd": "https://s53.nysdot.skyvdn.com:443/rtplive/R10_174/playlist.m3u8",
        "CIP south of West Alley Road": "https://s53.nysdot.skyvdn.com:443/rtplive/R10_175/playlist.m3u8",
    },

    # ====================================================
    # Grand Central Parkway
    # ====================================================
    "Grand Central Parkway (GCP)": {
        "GCP at Springfield Blvd": "https://s53.nysdot.skyvdn.com:443/rtplive/R10_054/playlist.m3u8",
        "GCP EB at Exit to CVE (I-295 NB)": "https://s53.nysdot.skyvdn.com:443/rtplive/R10_055/playlist.m3u8",
        "GCP at Cross Island Pkwy": "https://s53.nysdot.skyvdn.com:443/rtplive/R10_056/playlist.m3u8",
    },

    # ====================================================
    # 907M Local Queens Streets
    # ====================================================
    "Queens Local Streets (907M Corridor) — Served by Q18 / Q23 / Q49 / Q66 / Q70-SBS / Q72 / Q101 / Q102": {
        "907M at 94 Street": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_244/playlist.m3u8",
        "907M at WB I-278 / BQE Ramp": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_245/playlist.m3u8",
        "907M at 102 Street": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_246/playlist.m3u8",
        "907M at 44th Street": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_249/playlist.m3u8",
        "907M at 37th Street": "https://s53.nysdot.skyvdn.com:443/rtplive/R11_111/playlist.m3u8",
        "907M at 46th Street": "https://s53.nysdot.skyvdn.com:443/rtplive/R11_112/playlist.m3u8",
        "907M at 72nd Street": "https://s53.nysdot.skyvdn.com:443/rtplive/R11_113/playlist.m3u8",
        "907M at 75th Street": "https://s53.nysdot.skyvdn.com:443/rtplive/R11_114/playlist.m3u8",
        "907M at 27th Avenue": "https://s53.nysdot.skyvdn.com:443/rtplive/R11_116/playlist.m3u8",
        "907M at Ditmars Blvd": "https://s53.nysdot.skyvdn.com:443/rtplive/R11_117/playlist.m3u8",
    },

    # ====================================================
    # I-495 LIE
    # ====================================================
    "I-495 Long Island Expressway (LIE) — Highway Traffic Cameras": {
        "I-495 at 254th Street": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_155/playlist.m3u8",
        "I-495 at 220th Street": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_154/playlist.m3u8",
        "I-495 at 228th Street": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_255/playlist.m3u8",
        "I-495 ramp to Westbound I-278": "https://s7.nysdot.skyvdn.com:443/rtplive/R11_232/playlist.m3u8",
        "I-495 ramp from Eastbound BQE": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_132/playlist.m3u8",
        "I-495 at 48th Street / Lower Level": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_134/playlist.m3u8",
        "I-495 between 50th & 58th Street": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_135/playlist.m3u8",
        "I-495 at 58th Street / Lower Level": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_136/playlist.m3u8",
        "I-495 at 60th Street": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_137/playlist.m3u8",
        "I-495 at Grand Avenue": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_138/playlist.m3u8",
        "I-495 at 75th Street": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_139/playlist.m3u8",
        "I-495 at 84th Street": "https://s52.nysdot.skyvdn.com:443/rtplive/R11_140/playlist.m3u8",
    },
}

# =========================================================
# Flatten for single dropdown（Live Camera Feed had things in it）
# =========================================================

CAMERA_STREAMS = {
    f"[{group}] {cam}": url
    for group, cams in CAMERA_STREAM_GROUPS.items()
    for cam, url in cams.items()
}

# =========================================================
# AI Detection：with fake metrics.csv，to make sure everything work
# =========================================================

def run_detection_for_dashboard(camera_url, max_seconds=5, max_frames=30):
    records = []
    now = datetime.now(timezone.utc)

    for i in range(max_frames):
        ts = (now + pd.Timedelta(seconds=i)).isoformat()
        cars = randint(5, 30)
        buses = randint(0, 3)
        trucks = randint(0, 5)
        records.append({"ts": ts, "cars": cars, "buses": buses, "trucks": trucks})

    df = pd.DataFrame(records)
    df.to_csv("metrics.csv", index=False)
    return len(records)

# =========================================================
# Weather & News 
# =========================================================

def weather_style():
    return {
        "padding": "10px",
        "fontSize": "15px",
        "lineHeight": "1.6",
        "backgroundColor": "rgba(255,255,255,0.05)",
        "borderRadius": "8px",
        "marginTop": "10px",
    }

def news_style():
    return {
        "padding": "10px",
        "fontSize": "14px",
        "lineHeight": "1.5",
        "backgroundColor": "rgba(255,255,255,0.05)",
        "borderRadius": "8px",
        "marginTop": "10px",
        "maxHeight": "240px",
        "overflowY": "auto",
    }

# =========================================================
# Dash App
# =========================================================

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SLATE],
    serve_locally=True
)
app.title = "NYC Transit Intelligence Dashboard"

card_style = {
    "backgroundColor": "#181818",
    "border": "1px solid #333",
    "borderRadius": "14px",
    "boxShadow": "0 4px 14px rgba(0,0,0,0.45)",
    "padding": "18px",
    "marginBottom": "18px",
    "fontFamily": "Segoe UI, Roboto, Helvetica, Arial, sans-serif",
    "color": "#e5e5e5",
    "fontSize": "15px",
    "letterSpacing": "0.3px",
}

# =========================================================
# FRONTFACE + MAIN DASHBOARD WRAPPER
# =========================================================

app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),

    # ======= FRONTFACE =======
    html.Div(
        id="frontface",
        children=[

            # dark overlay
            html.Div(
                style={
                    "position": "absolute",
                    "top": 0,
                    "left": 0,
                    "width": "100%",
                    "height": "100%",
                    "background": (
                        "linear-gradient(to bottom, rgba(0,0,0,0.55), rgba(0,0,0,0.85))"
                    ),
                    "zIndex": 1,
                }
            ),

            # inside content
            html.Div(
                [
                    # NYC Subway style icon (MTA circle logo feel)
                    html.Div(
                        "MTA",
                        style={
                            "width": "110px",
                            "height": "110px",
                            "borderRadius": "50%",
                            "backgroundColor": "#0039A6",
                            "color": "white",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "fontSize": "36px",
                            "fontWeight": "800",
                            "margin": "0 auto 25px auto",
                            "boxShadow": "0 0 22px rgba(0,60,130,0.9)",
                            "fontFamily": "Helvetica Neue, Helvetica, Arial, sans-serif",
                        }
                    ),

                    # main title
                    html.H1(
                        "NYC Transit Intelligence System",
                        style={
                            "fontSize": "50px",
                            "fontWeight": "800",
                            "color": "white",
                            "zIndex": 2,
                            "position": "relative",
                            "marginBottom": "16px",
                            "textShadow": "0 4px 16px rgba(0,0,0,0.65)",
                            "fontFamily": "Helvetica Neue, Helvetica, Arial, sans-serif",
                            "opacity": 0,
                            "animation": "fadein 1.4s ease forwards",
                        }
                    ),

                    # subtitle
                    html.H4(
                        "Real-time Bus Maps • Live Video • AI Traffic Detection",
                        style={
                            "color": "white",
                            "zIndex": 2,
                            "position": "relative",
                            "margin": "0 auto 12px auto",
                            "fontSize": "22px",
                            "lineHeight": "1.4",
                            "maxWidth": "720px",
                            "textShadow": "0 2px 12px rgba(0,0,0,0.65)",
                            "fontFamily": "Helvetica Neue, Helvetica, Arial, sans-serif",
                            "opacity": 0,
                            "animation": "fadein 2s ease forwards",
                        }
                    ),

                    # tag line
                    html.P(
                        "From Bus Stop to Bottleneck: See the City's Pulse with AI Traffic.",
                        style={
                            "color": "rgba(255,255,255,0.9)",
                            "zIndex": 2,
                            "position": "relative",
                            "margin": "0 auto 40px auto",
                            "fontSize": "17px",
                            "lineHeight": "1.5",
                            "maxWidth": "720px",
                            "fontStyle": "italic",
                            "letterSpacing": "0.4px",
                            "textShadow": "0 2px 10px rgba(0,0,0,0.6)",
                            "fontFamily": "Helvetica Neue, Helvetica, Arial, sans-serif",
                            "opacity": 0,
                            "animation": "fadein 2.3s ease forwards",
                        }
                    ),

                    # button
                    dbc.Button(
                        "Enter Dashboard",
                        id="enter-btn",
                        color="primary",
                        size="lg",
                        style={
                            "padding": "14px 38px",
                            "borderRadius": "12px",
                            "fontSize": "22px",
                            "fontWeight": "700",
                            "backgroundColor": "#0039A6",
                            "border": "2px solid #0050D0",
                            "boxShadow": "0 0 18px rgba(0,80,200,0.7)",
                            "zIndex": 2,
                            "position": "relative",
                            "opacity": 0,
                            "animation": "fadein 2.6s ease forwards",
                        }
                    ),
                ],
                style={
                    "textAlign": "center",
                    "position": "absolute",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                    "zIndex": 2,
                },
            ),
        ],
        style={
            "height": "100vh",
            "backgroundImage": "url('https://images.unsplash.com/photo-1488748605490-4d49b97fbb26')",
            "backgroundSize": "cover",
            "backgroundPosition": "center",
            "position": "relative",
            "animation": "fadein_bg 1s ease forwards",
        },
    ),

    # ======= MAIN DASHBOARD =======
    html.Div(
        id="main-dashboard",
        children=[

            html.H2(
                "🚦 NYC Transit Intelligence Dashboard",
                className="text-center my-3 text-light fw-bold"
            ),

            dbc.Row([
                # ================= LEFT: Route + Maps + Weather + News + AD =================
                dbc.Col([
                    html.Div([
                        # Bus Route Selector
                        html.Label(
                            "🚌 Select Bus Route:",
                            className="text-light fw-bold mb-2"
                        ),

                        dcc.Dropdown(
                            id="route-select",
                            options=[
                                {"label": "Q18 – Astoria ↔ Maspeth", "value": "Q18.png"},
                                {"label": "Q23 – East Elmhurst ↔ Forest Hills", "value": "Q23.png"},
                                {"label": "Q25 – College Point ↔ Jamaica", "value": "Q25.png"},
                                {"label": "Q49 – East Elmhurst ↔ Jackson Heights", "value": "Q49.png"},
                                {"label": "Q66 – Flushing ↔ Long Island City", "value": "Q66.png"},
                                {"label": "Q70-SBS – LaGuardia Link", "value": "Q70.png"},
                                {"label": "Q72 – LaGuardia Airport ↔ Rego Park", "value": "Q72.png"},
                                {"label": "Q101 – Steinway ↔ Hunters Point", "value": "Q101.png"},
                                {"label": "Q102 – Roosevelt Island ↔ Long Island City", "value": "Q102.png"},
                            ],
                            value="Q25.png",
                            clearable=False,
                            style={"color": "#000"}
                        ),

                        #maps
                        html.Div(
                            id="map-container",
                            children=dcc.Loading(
                                id="map-loading",
                                type="default",
                                children=dbc.Row([
                                    dbc.Col(
                                        html.Img(
                                            id="route-map",
                                            src=app.get_asset_url("Q25.png"),
                                            style={
                                                "width": "100%",
                                                "height": "auto",
                                                "objectFit": "contain",
                                                "borderRadius": "10px",
                                                "border": "1px solid #333",
                                            }
                                        ),
        
                                    ),
                                ])
                            ),
                            style={"marginTop": "8px"},
                        ),

                        # Weather
                        html.Div(id="weather-box", className="text-light mt-3"),
                        dcc.Interval(id="weather-refresh", interval=600_000, n_intervals=0),

                        # News
                        html.Div(id="news-box", className="text-light mt-3"),
                        dcc.Interval(id="news-refresh", interval=1_800_000, n_intervals=0),

                        # AD interval
                        dcc.Interval(id="ad-refresh", interval=8000, n_intervals=0),

                        # === Floating AD Box  ===
html.Div([
    # open
    html.Div(
        id="ad-expanded",
        children=[
            html.Div([
                html.Span("📢 Opportunities in NYC Transit",
                          style={"fontWeight": "bold", "fontSize": "16px"}),
                html.Span("✖", id="ad-close", n_clicks=0, style={
                    "float": "right",
                    "cursor": "pointer",
                    "fontWeight": "bold",
                    "fontSize": "16px",
                })
            ]),
            html.Div(id="ad-content", style={
                "fontSize": "14px",
                "marginTop": "6px"
            }),
            html.A(
                "Apply Now",
                id="ad-link",
                href="https://www.mta.info/careers",
                target="_blank",
                style={
                    "display": "inline-block",
                    "marginTop": "8px",
                    "padding": "6px 14px",
                    "backgroundColor": "#1d71bf",
                    "color": "white",
                    "borderRadius": "6px",
                    "textDecoration": "none",
                    "fontSize": "13px",
                    "fontWeight": "600",
                }
            )
        ],
        style={
            "position": "fixed",
            "left": "20px",
            "bottom": "20px",
            "width": "260px",
            "backgroundColor": "rgba(20,20,20,0.85)",
            "border": "1px solid #333",
            "borderRadius": "12px",
            "padding": "14px",
            "color": "white",
            "zIndex": "9999",
            "boxShadow": "0 4px 18px rgba(0,0,0,0.5)",
            "backdropFilter": "blur(8px)",
        }
    ),

    # close
    html.Div(
        id="ad-collapsed",
        children="📢",
        n_clicks=0,
        style={
            "position": "fixed",
            "left": "20px",
            "bottom": "20px",
            "width": "50px",
            "height": "50px",
            "backgroundColor": "rgba(20,20,20,0.7)",
            "borderRadius": "50%",
            "display": "none",
            "justifyContent": "center",
            "alignItems": "center",
            "fontSize": "24px",
            "cursor": "pointer",
            "color": "white",
            "zIndex": "9999",
            "boxShadow": "0 4px 18px rgba(0,0,0,0.4)",
        }
    ),
]),


                    ], style=card_style)
                ], md=6),

                # right：Camera + AI Detection + Graph + Advice
                dbc.Col([
                    html.Div([
                        html.H4(
                            "🎥 Live Camera Feed",
                            className="text-center text-light mb-3 fw-bold"
                        ),

                        dcc.Dropdown(
                            id="camera-select",
                            options=[{"label": k, "value": v} for k, v in CAMERA_STREAMS.items()],
                            value=list(CAMERA_STREAMS.values())[0],
                            clearable=False,
                            style={"color": "#000"}
                        ),

                        html.Video(
                            id="video-player",
                            src=list(CAMERA_STREAMS.values())[0],
                            controls=True,
                            autoPlay=True,
                            muted=True,
                            style={
                                "width": "100%",
                                "height": "280px",
                                "border": "2px solid #555"
                            }
                        ),
                    ], style=card_style),

                    html.Div([
                        dbc.Button(
                            "Run AI Detection",
                            id="run-detect",
                            color="warning",
                            className="w-100 mb-2"
                        ),

                        html.Div(
                            id="run-status",
                            className="text-light mb-2"
                        ),

                        dcc.Interval(
                            id="refresh",
                            interval=5_000,
                            n_intervals=0
                        ),

                        dcc.Graph(
                            id="metrics-graph",
                            style={"height": "300px"}
                        ),

                        html.Div(
                            id="traffic-advice-box",
                            children=[
                                html.Div(
                                    "💡 Run AI Detection to see live traffic insights.",
                                    style={
                                        "fontWeight": "600",
                                        "fontSize": "16px",
                                        "marginBottom": "4px"
                                    }
                                ),
                                html.Div(
                                    "After at least one detection run, this panel will summarize congestion level and suggest routes.",
                                    style={"fontSize": "13px", "opacity": 0.85}
                                ),
                            ],
                            style={
                                "backgroundColor": "rgba(10,45,90,0.85)",
                                "padding": "14px",
                                "borderRadius": "10px",
                                "border": "1px solid rgba(255,255,255,0.25)",
                                "marginTop": "10px",
                                "boxShadow": "0 0 14px rgba(0,0,0,0.45)"
                            }
                        ),
                        # === ETA MODULE UI ===
html.Div(
    id="eta-box",
    children=[
        html.H5("🕒 Bus Arrival Estimation", className="text-light fw-bold"),
        html.Div(id="eta-content", className="text-light", style={"fontSize": "14px"}),
    ],
    style={
        "backgroundColor": "rgba(255,255,255,0.05)",
        "padding": "12px",
        "borderRadius": "10px",
        "marginTop": "12px",
    }
),
                        # === DELAY PREDICTION UI ===
html.Div(
    id="delay-box",
    children=[
        html.H5("⚠️ Delay Prediction", className="text-light fw-bold"),
        html.Div(id="delay-content", className="text-light", style={"fontSize": "14px"}),
    ],
    style={
        "backgroundColor": "rgba(255,255,255,0.05)",
        "padding": "12px",
        "borderRadius": "10px",
        "marginTop": "12px",
    }
),
                        # === ALTERNATIVE ROUTE UI ===
html.Div(
    id="alt-route-box",
    children=[
        html.H5("🛤 Alternative Route Recommendation", className="text-light fw-bold"),
        html.Div(id="alt-route-content", className="text-light", style={"fontSize": "14px"}),
    ],
    style={
        "backgroundColor": "rgba(255,255,255,0.05)",
        "padding": "12px",
        "borderRadius": "10px",
        "marginTop": "12px",
    }
),
                        # === BUS PERFORMANCE UI ===
    html.Div(
        id="bus-perf-box",
        children=[
            html.H5("🚍 Bus Performance Estimation", className="text-light fw-bold"),
            html.Div(id="bus-perf-content", className="text-light", style={"fontSize": "14px"}),
        ],
        style={
            "backgroundColor": "rgba(255,255,255,0.05)",
            "padding": "12px",
            "borderRadius": "10px",
            "marginTop": "12px",
        }
),

                    ], style=card_style)
                ], md=6)
            ])
        ],
        style={"display": "none"}  # hide dashboard
    )

], fluid=True, style={"backgroundColor": "#121212"})

# ==== Helpers for traffic advice ==================================

#URL to corridor/group
CAMERA_URL_TO_GROUP = {}
for group_name, cams in CAMERA_STREAM_GROUPS.items():
    for cam_label, cam_url in cams.items():
        CAMERA_URL_TO_GROUP[cam_url] = group_name

# each corridor suggestion
BUS_SUGGESTIONS = {
    "I-678 Van Wyck Expressway — Served by Q25":
        "For local access along Van Wyck, consider Q25 toward Jamaica or College Point depending on your direction.",
    "I-278 (BQE) Queens Section — Served by Q18 / Q66":
        "For Queens–Manhattan connectivity, consider Q18 (Astoria–Maspeth) or Q66 (Flushing–LIC).",
    "I-295 / Cross Island Parkway":
        "Cross Island Pkwy has limited bus coverage. Consider nearby Q27 / Q30 corridors where available.",
    "Grand Central Parkway (GCP)":
        "GCP is mostly highway. Check nearby local routes (Q23, Q72, etc.) for parallel service.",
    "Queens Local Streets (907M Corridor) — Served by Q18 / Q23 / Q49 / Q66 / Q70-SBS / Q72 / Q101 / Q102":
        "This corridor is well served: Q18, Q23, Q49, Q66, Q70-SBS, Q72, Q101, Q102. Consider SBS or limited routes for faster service.",
    "I-495 Long Island Expressway (LIE) — Highway Traffic Cameras":
        "LIE has no Q-bus running on the mainline. Use park-and-ride or connect via local Q routes near interchanges.",
}

# =========================================================
# Callbacks
# =========================================================

# camera select
@app.callback(
    Output("video-player", "src"),
    Input("camera-select", "value")
)
def update_cam(v):
    return v


# refresh metrics 
@app.callback(
    Output("metrics-graph", "figure"),
    Input("refresh", "n_intervals")
)
def update_metrics(_):
    if not os.path.exists("metrics.csv"):
        return px.line(title="Waiting for detection...", template="plotly_dark")

    df = pd.read_csv("metrics.csv")
    if df.empty:
        return px.line(title="No data yet", template="plotly_dark")

    fig = px.line(
        df,
        x="ts",
        y=["cars", "buses", "trucks"],
        title="Vehicle Counts",
        markers=True,
        template="plotly_dark"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig


# click to run detyection generate metrics.csv
@app.callback(
    Output("run-status", "children"),
    Input("run-detect", "n_clicks"),
    State("camera-select", "value"),
    prevent_initial_call=True
)
def run_once(n, cam_url):
    count = run_detection_for_dashboard(cam_url)
    if count == 0:
        return "❌ Detection failed."
    return f"✅ Completed {count} frames."


# weather
@app.callback(
    Output("weather-box", "children"),
    Input("weather-refresh", "n_intervals")
)
def update_weather(_):
    try:
        url = "https://wttr.in/Queens?format=j1"
        res = requests.get(url, timeout=6).json()

        temp = res["current_condition"][0]["temp_F"] + "°F"
        wind = res["current_condition"][0]["windspeedMiles"] + " mph"
        desc = res["current_condition"][0]["weatherDesc"][0]["value"]

        wind_emoji = "🌬️"
        if "north" in desc.lower(): wind_emoji = "⬆️"
        elif "south" in desc.lower(): wind_emoji = "⬇️"
        elif "east" in desc.lower(): wind_emoji = "➡️"
        elif "west" in desc.lower(): wind_emoji = "⬅️"

        return [
            html.H5("🌤 Current Weather (Queens)", className="fw-bold"),
            html.Div(f"🌡 Temperature: {temp}"),
            html.Div(f"{wind_emoji} Wind: {wind}"),
            html.Div(f"📌 Condition: {desc}"),
        ]
    except:
        return html.Div("🌫 Weather unavailable", className="text-warning")


# news
@app.callback(
    Output("news-box", "children"),
    Input("news-refresh", "n_intervals")
)
def update_news(_):
    try:
        feed_url = "https://rss.nytimes.com/services/xml/rss/nyt/NYRegion.xml"
        feed = feedparser.parse(feed_url)

        items = []
        for entry in feed.entries[:5]:
            items.append(
                html.Div([
                    html.A(entry.title, href=entry.link, target="_blank",
                           style={"color": "#4da3ff", "textDecoration": "none"}),
                    html.Div(entry.published, style={"fontSize": "11px", "opacity": 0.7}),
                    html.Hr(style={"borderColor": "#444"})
                ])
            )

        return html.Div([
            html.Div("📰 NYC Transit / Local News",
                     style={"fontSize": "16px", "fontWeight": "bold", "marginBottom": "6px"}),
            *items
        ], style=news_style())
    except:
        return html.Div("📰 Unable to load news feed.", style=news_style())


# =========================================================
# AI Traffic Intelligence
# =========================================================
@app.callback(
    Output("traffic-advice-box", "children"),
    [Input("refresh", "n_intervals"),
     Input("camera-select", "value")]
)
def update_traffic_advice(n, cam_url):
    # If no detection yet
    if n is None or not os.path.exists("metrics.csv"):
        return [
            html.Div(
                "💡 Run AI Detection to see live traffic insights.",
                style={"fontWeight": "600", "fontSize": "16px", "marginBottom": "4px"}
            ),
            html.Div(
                "After at least one detection run, this panel will summarize congestion level and suggest routes.",
                style={"fontSize": "13px", "opacity": 0.85},
            ),
        ]

    try:
        df = pd.read_csv("metrics.csv")
    except:
        return [
            html.Div("⚠ Unable to read metrics file.", style={"fontWeight": "600"}),
            html.Div("Please run AI Detection again.", style={"fontSize": "13px"}),
        ]

    if df.empty:
        return [
            html.Div("📉 No vehicle data yet.", style={"fontWeight": "600"}),
            html.Div("Run AI Detection to start collecting traffic metrics.",
                     style={"fontSize": "13px"}),
        ]

    tail = df.tail(5).copy()

    current = int(tail.iloc[-1]["cars"])
    recent_avg = float(tail["cars"].mean())

    # Traffic level
    if current < 10:
        level = "Low"
        icon = "🟢"
        text = "Free-flow traffic."
    elif current < 25:
        level = "Medium"
        icon = "🟡"
        text = "Moderate traffic with some slowdowns."
    else:
        level = "High"
        icon = "🔴"
        text = "Heavy congestion expected."

    # Trend & simple prediction
    if len(tail) >= 2:
        prev_avg = float(tail["cars"].iloc[:-1].mean())
    else:
        prev_avg = recent_avg

    if current > prev_avg * 1.1:
        trend = "increasing"
        factor = 1.15
    elif current < prev_avg * 0.9:
        trend = "decreasing"
        factor = 0.90
    else:
        trend = "stable"
        factor = 1.00

    predicted_5m = int(round(current * factor))

    # Time band
    hour = datetime.now().hour
    if 7 <= hour < 10:
        period = "AM peak (07:00–10:00)"
    elif 16 <= hour < 19:
        period = "PM peak (16:00–19:00)"
    else:
        period = "Off-peak period"

    # Corridor + bus suggestions
    corridor = CAMERA_URL_TO_GROUP.get(cam_url, "Selected corridor")
    bus_suggestion = BUS_SUGGESTIONS.get(
        corridor, "Use nearby Q routes or subway as alternatives."
    )

    return [
        html.Div(
            f"{icon} Current Traffic Level: {level}",
            style={"fontWeight": "700", "fontSize": "16px", "marginBottom": "4px"}
        ),
        html.Div(text, style={"fontSize": "13px", "marginBottom": "8px"}),
        html.Div(f"⏱ Time band: {period}", style={"fontSize": "13px"}),
        html.Div(
            f"🚗 Vehicles detected: {current} (avg {recent_avg:.1f} across last {len(tail)} points)",
            style={"fontSize": "13px"}
        ),
        html.Div(
            f"📈 Trend: {trend} → predicted {predicted_5m} in 5 minutes.",
            style={"fontSize": "13px", "marginBottom": "8px"}
        ),
        html.Div(f"🚌 Corridor: {corridor}", style={"fontSize": "13px"}),
        html.Div(
            f"✅ Route suggestion: {bus_suggestion}",
            style={"fontSize": "13px", "marginBottom": "8px"}
        ),
        html.Div("🌦 Weather impact: neutral (simple model).",
                 style={"fontSize": "13px", "opacity": 0.85})
    ]

#Frontface
@app.callback(
    Output("frontface", "style"),
    Output("main-dashboard", "style"),
    Input("enter-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_dashboard(n):

    frontface_hide = {
        "display": "none"
    }

    dashboard_show = {
        "display": "block",
        "opacity": 1,
        "animation": "slideup 0.8s ease forwards",
        "backgroundColor": "#121212"
    }

    return frontface_hide, dashboard_show
#ETA
@app.callback(
    Output("eta-content", "children"),
    Input("camera-select", "value"),
    Input("refresh", "n_intervals")
)
def update_eta(cam_url, _):
    corridor = CAMERA_URL_TO_GROUP.get(cam_url, "Unknown")

    base_eta = random.randint(4, 10)

    if os.path.exists("metrics.csv"):
        df = pd.read_csv("metrics.csv")
        if not df.empty:
            cars = df.tail(1).iloc[0]["cars"]
            if cars > 28:
                base_eta += 6
            elif cars > 18:
                base_eta += 3

    return [
        html.Div(f"Corridor: {corridor}"),
        html.Div(f"Estimated bus arrival: ~{base_eta} min"),
    ]
    
#Delay Prediction Callback
@app.callback(
    Output("delay-content", "children"),
    Input("refresh", "n_intervals"),
    Input("camera-select", "value")
)
def update_delay(_, cam_url):

    corridor = CAMERA_URL_TO_GROUP.get(cam_url, "Unknown Corridor")

    if not os.path.exists("metrics.csv"):
        return "Run AI Detection to enable delay prediction."

    df = pd.read_csv("metrics.csv")
    if df.empty:
        return "Not enough data."

    tail = df.tail(6)
    cars = tail["cars"].iloc[-1]

    if cars < 10:
        delay = 0
    elif cars < 20:
        delay = 2
    elif cars < 30:
        delay = 5
    else:
        delay = 10

    return [
        html.Div(f"Corridor: {corridor}"),
        html.Div(f"Predicted Delay: {delay} minutes"),
    ]


#Recommendation
@app.callback(
    Output("alt-route-content", "children"),
    Input("refresh", "n_intervals"),
    Input("camera-select", "value")
)
def recommend_alt(_, cam_url):

    corridor = CAMERA_URL_TO_GROUP.get(cam_url, "")

    if not os.path.exists("metrics.csv"):
        return "Waiting for detection data."

    df = pd.read_csv("metrics.csv")
    if df.empty:
        return "Not enough data to generate recommendations."

    cars = df.tail(1).iloc[0]["cars"]

    alternatives = {
        "I-678 Van Wyck Expressway — Served by Q25":
            ("Q44-SBS", "E/F subway at Jamaica"),
        "I-278 (BQE) Queens Section — Served by Q18 / Q66":
            ("Q66 local", "N/W subway at Astoria"),
        "I-495 Long Island Expressway (LIE) — Highway Traffic Cameras":
            ("Q30/Q17", "E subway at Queens Blvd"),
    }

    alt = alternatives.get(corridor, ("Check nearby subway", "Consider walking 5–10 mins"))

    if cars > 25:
        action = f"Heavy congestion detected → Recommend switching to {alt[1]}"
    elif cars > 15:
        action = f"Moderate congestion → Consider {alt[0]}"
    else:
        action = "Traffic conditions are normal."

    return [
        html.Div(f"Corridor: {corridor}"),
        html.Div(action),
    ]

#Bus Performance

@app.callback(
    Output("bus-perf-content", "children"),
    Input("refresh", "n_intervals"),
    Input("camera-select", "value")
)
def bus_performance(_, cam_url):

    corridor = CAMERA_URL_TO_GROUP.get(cam_url, "Unknown Corridor")

    if not os.path.exists("metrics.csv"):
        return "Run detection to enable performance model."

    df = pd.read_csv("metrics.csv")
    if df.empty:
        return "Not enough data."

    cars = df.tail(1).iloc[0]["cars"]

    if cars < 10:
        speed = 18
    elif cars < 18:
        speed = 12
    elif cars < 28:
        speed = 8
    else:
        speed = 4

    delay = max(0, int((18 - speed) * 0.8))

    return [
        html.Div(f"Corridor: {corridor}"),
        html.Div(f"Estimated Bus Speed: {speed} mph"),
        html.Div(f"Expected Delay: {delay} minutes"),
    ]

#AD
@app.callback(
    Output("ad-content", "children"),
    Output("ad-link", "href"),
    Input("ad-refresh", "n_intervals")
)
def update_ads(n):
    ads = [
        (
            "🚌 MTA hiring Bus Operators — Full-time roles available.",
            "https://careers.mta.org/operations"
        ),
        (
            "🛠️ NYC Transit recruiting Maintenance Technicians.",
            "https://careers.mta.org/technical"
        ),
        (
            "📊 NYC DOT opening Data Analyst Intern positions.",
            "https://www.nyc.gov/site/dot/about/careers.page"
        ),
        (
            "🚇 Become a Subway Conductor — Paid training included.",
            "https://careers.mta.org/operations"
        ),
        (
            "💼 Queens Tech startup hiring Python/Dash developers.",
            "https://www.google.com/search?q=Queens+tech+jobs"
        ),
        (
            "🧭 Port Authority of NY/NJ opening Airport Operations Intern roles.",
            "https://www.panynj.gov/port-authority/en/careers.html"
        )
    ]

    idx = n % len(ads)
    return ads[idx][0], ads[idx][1]
    
@app.callback(
    Output("ad-expanded", "style"),
    Output("ad-collapsed", "style"),
    Input("ad-close", "n_clicks"),
    Input("ad-collapsed", "n_clicks")
)
def toggle_ad(close_clicks, expand_clicks):

    expanded_style = {
        "position": "fixed",
        "left": "20px",
        "bottom": "20px",
        "width": "260px",
        "backgroundColor": "rgba(20,20,20,0.85)",
        "border": "1px solid #333",
        "borderRadius": "12px",
        "padding": "14px",
        "color": "white",
        "zIndex": "9999",
        "boxShadow": "0 4px 18px rgba(0,0,0,0.5)",
        "backdropFilter": "blur(8px)",
        "display": "block"
    }

    collapsed_style = {
        "position": "fixed",
        "left": "20px",
        "bottom": "20px",
        "width": "50px",
        "height": "50px",
        "backgroundColor": "rgba(20,20,20,0.7)",
        "borderRadius": "50%",
        "justifyContent": "center",
        "alignItems": "center",
        "fontSize": "24px",
        "cursor": "pointer",
        "color": "white",
        "zIndex": "9999",
        "boxShadow": "0 4px 18px rgba(0,0,0,0.4)",
        "display": "none",
    }

    # Close → collapse
    if close_clicks and close_clicks > expand_clicks:
        expanded_style["display"] = "none"
        collapsed_style["display"] = "flex"

    # Re-expand
    if expand_clicks and expand_clicks >= close_clicks:
        expanded_style["display"] = "block"
        collapsed_style["display"] = "none"

    return expanded_style, collapsed_style

#map road
@app.callback(
    Output("route-map", "src"),
    Input("route-select", "value")
)
def update_map(selected_png):
    return app.get_asset_url(selected_png)


# =========================================================
# U:HuggingFace Spaces
# =========================================================

if __name__ == "__main__":
    # HF Spaces  7860，set host=0.0.0.0 
    app.run_server(host="0.0.0.0", port=7860, debug=False)
