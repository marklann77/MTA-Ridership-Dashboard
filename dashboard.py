# Used AI to translate my notebook into this Python file, which made it easier to serve as a Panel dashboard.

import panel as pn
import pandas as pd
import matplotlib.pyplot as plt
import folium

pn.extension()

# -----------------------------------------
# GLOBAL STYLING
# -----------------------------------------

pn.config.raw_css.append("""
body {
    background-color: #0f1b2b;
}
""")

# -----------------------------------------
# LOAD DATA
# -----------------------------------------

df = pd.read_csv(
    "MTA_Daily_Ridership_Data__2020_-_2025_20250304.csv",
    parse_dates=["Date"]
)

df_stations = pd.read_csv(
    "MTA_Subway_Stations_20250304.csv"
)

df_top10 = pd.read_csv(
    "2024 Top 10 Busiest MTA Subways Stations - Sheet1.csv"
)

# -----------------------------------------
# EXTRACT LAT / LON
# -----------------------------------------

df_stations["lon"] = df_stations["Georeference"].str.extract(
    r"POINT \(([-\d\.]+)"
)[0].astype(float)

df_stations["lat"] = df_stations["Georeference"].str.extract(
    r"POINT \([-\d\.]+ ([-\d\.]+)\)"
)[0].astype(float)

df_top10["lon"] = df_top10["Georeference"].str.extract(
    r"POINT \(([-\d\.]+)"
)[0].astype(float)

df_top10["lat"] = df_top10["Georeference"].str.extract(
    r"POINT \([-\d\.]+ ([-\d\.]+)\)"
)[0].astype(float)

# -----------------------------------------
# AUTHOR BOX
# -----------------------------------------

author_box = pn.pane.Markdown(
    """
<div style="background:#d9d9d9;padding:30px;border-radius:6px;text-align:center;">
  <div style="font-size:26px;font-weight:700;">Author: Mark Lannaman</div>
  <div style="font-size:16px;margin-top:6px;">NYC MTA Subway Ridership</div>
</div>
""",
    width=420,
    sizing_mode="fixed"
)

# -----------------------------------------
# TOP 10 DROPDOWN
# -----------------------------------------

df_top10_sorted = df_top10.sort_values("Ridership", ascending=False)

top10_dropdown = pn.widgets.Select(
    name="Top 10 busiest stations",
    options=[
        f"{i+1}. {row['Station/complex']}"
        for i, (_, row) in enumerate(df_top10_sorted.iterrows())
    ],
    width=420
)

# -----------------------------------------
# SUMMARY METRICS
# -----------------------------------------

busiest_day = df.loc[df["Subways: Total Estimated Ridership"].idxmax()]

busiest_day_box = pn.pane.Markdown(
    f"""
<div style="background:#d9d9d9;padding:30px;border-radius:6px;text-align:center;">
  <div style="font-size:22px;font-weight:700;">Busiest Day</div>
  <div>{busiest_day['Date'].date()}</div>
  <div>{int(busiest_day['Subways: Total Estimated Ridership']):,} riders</div>
</div>
""",
    width=420,
    sizing_mode="fixed"
)

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

busiest_month = (
    df.groupby(["Year", "Month"])["Subways: Total Estimated Ridership"]
    .sum()
    .idxmax()
)

busiest_month_box = pn.pane.Markdown(
    f"""
<div style="background:#d9d9d9;padding:30px;border-radius:6px;text-align:center;">
  <div style="font-size:22px;font-weight:700;">Busiest Month</div>
  <div>{busiest_month[1]}/{busiest_month[0]}</div>
</div>
""",
    width=420,
    sizing_mode="fixed"
)

avg_daily = int(df["Subways: Total Estimated Ridership"].mean())

avg_ridership_box = pn.pane.Markdown(
    f"""
<div style="background:#d9d9d9;padding:30px;border-radius:6px;text-align:center;">
  <div style="font-size:22px;font-weight:700;">Avg Daily Ridership</div>
  <div>{avg_daily:,}</div>
</div>
""",
    width=420,
    sizing_mode="fixed"
)

# -----------------------------------------
# MAP
# -----------------------------------------

m = folium.Map(
    location=[40.78, -73.94],
    zoom_start=12,
    tiles="Cartodb Positron"
)

# all stations (blue)
for _, r in df_stations.iterrows():
    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=3,
        color="blue",
        fill=True,
        fill_opacity=0.6,
    ).add_to(m)

# top 10 stations (red)
for _, r in df_top10.iterrows():
    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=7,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.9,
    ).add_to(m)

folium_pane = pn.pane.plot.Folium(m, height=500)

# -----------------------------------------
# RIDERSHIP PLOT
# -----------------------------------------

df["ridership_7d"] = df["Subways: Total Estimated Ridership"].rolling(7).mean()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Date"], df["ridership_7d"])
ax.set_title("7-Day Average Subway Ridership")

ridership_pane = pn.pane.Matplotlib(fig, tight=True)

# -----------------------------------------
# LAYOUT
# -----------------------------------------

left_column = pn.Column(
    author_box,
    top10_dropdown,
    busiest_month_box,
    busiest_day_box,
    avg_ridership_box,
    width=420,
    styles={"padding": "10px"}
)

right_column = pn.Column(
    folium_pane,
    ridership_pane,
    width=850,
    sizing_mode="fixed"
)

dashboard = pn.Row(
    pn.layout.Spacer(width=30),
    left_column,
    pn.layout.Spacer(width=30),
    right_column,
    sizing_mode="stretch_width",
    styles={"background": "#0f1b2b"}
)

dashboard.servable()


# -----------------------------------------
# SERVE
# -----------------------------------------

dashboard.servable()

