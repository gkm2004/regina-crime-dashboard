print("✅ app.py started")
from flask import Flask, render_template, request, jsonify
import pandas as pd
import folium

app = Flask(__name__)

# Coordinates dictionary (unchanged)
area_coords = {
    "Al Ritchie": [50.4384, -104.5963],
    "Albert Park": [50.4171, -104.6461],
    "Argyle Park": [50.4890, -104.6102],
    "Boothill": [50.4660, -104.6100],
    "Cathedral": [50.4483, -104.6217],
    "Centre Square": [50.4460, -104.6100],
    "Core Group": [50.4480, -104.6060],
    "Coronation Park": [50.4775, -104.6268],
    "Dewdney East": [50.4612, -104.5841],
    "Dieppe": [50.4671, -104.5930],
    "Eastview": [50.4545, -104.5789],
    "Gardiner Park": [50.4392, -104.5380],
    "Gladmer Park": [50.4489, -104.5820],
    "Hillsdale": [50.4236, -104.6240],
    "Lakeview": [50.4289, -104.6202],
    "Market Square": [50.4501, -104.6123],
    "McNab": [50.4644, -104.6167],
    "Mount Royal": [50.4701, -104.6644],
    "Normanview": [50.4709, -104.6580],
    "Normanview West": [50.4704, -104.6625],
    "North Central": [50.4635, -104.6239],
    "North East": [50.4842, -104.6044],
    "Prairie View": [50.4931, -104.6649],
    "Regent Park": [50.4864, -104.6425],
    "Rosemont": [50.4676, -104.6483],
    "Ross Industrial": [50.4812, -104.5961],
    "Rural": [50.4549, -104.7650],
    "Sherwood Estates": [50.4824, -104.6881],
    "Twin Lakes": [50.4849, -104.6830],
    "University Park": [50.4470, -104.5500],
    "Uplands": [50.4915, -104.5952],
    "Walsh Acres": [50.4960, -104.6490],
    "Warehouse District": [50.4556, -104.6003],
    "Wascana Park": [50.4300, -104.6171],
    "Whitmore Park": [50.4234, -104.6187],
}

# Main dashboard route
@app.route('/')
def dashboard():
    df = pd.read_csv("Crime2025.csv")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.drop(columns=['Total'], errors='ignore')
    melted = df.melt(id_vars=["Crime Classes"], var_name="Area", value_name="Count")
    melted = melted[melted["Count"] > 0]

    # Prepare pie chart data: total crime by area
    pie_data = melted.groupby("Area")["Count"].sum().reset_index()
    pie_rows = [[row["Area"], int(row["Count"])] for _, row in pie_data.iterrows()]

    m = folium.Map(
        location=[50.4452, -104.6189],
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='© CartoDB Dark Matter',
        zoom_start=12,
        min_zoom=11,
        max_zoom=16,
        max_bounds=True
    )

    for _, row in melted.iterrows():
        coords = area_coords.get(row["Area"])
        if coords:
            folium.CircleMarker(
                location=coords,
                radius=7 + row["Count"] * 0.3,
                color="red",
                fill=True,
                fill_color="red",
                popup=f"{row['Crime Classes']}: {int(row['Count'])} in {row['Area']}"
            ).add_to(m)

    map_html = m._repr_html_()
    areas = sorted(area_coords.keys())
    return render_template("index.html", map=map_html, areas=areas, pie_data=pie_rows)

# AJAX update route for area selection
@app.route('/update-area', methods=['POST'])
def update_area():
    data = request.get_json()
    selected_area = data.get('area', 'all')

    df = pd.read_csv("Crime2025.csv")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.drop(columns=['Total'], errors='ignore')
    melted = df.melt(id_vars=["Crime Classes"], var_name="Area", value_name="Count")
    melted = melted[melted["Count"] > 0]

    if selected_area != 'all':
        melted = melted[melted["Area"] == selected_area]

    m = folium.Map(
        location=[50.4452, -104.6189],
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='© CartoDB Dark Matter',
        zoom_start=12,
        min_zoom=11,
        max_zoom=16,
        max_bounds=True
    )

    for _, row in melted.iterrows():
        coords = area_coords.get(row["Area"])
        if coords:
            folium.CircleMarker(
                location=coords,
                radius=7 + row["Count"] * 0.3,
                color="red",
                fill=True,
                fill_color="red",
                popup=f"{row['Crime Classes']}: {int(row['Count'])} in {row['Area']}"
            ).add_to(m)

    return m._repr_html_()  # send updated map HTML to JS

@app.route('/get-pie-data', methods=['POST'])
def get_pie_data():
    data = request.get_json()
    selected_area = data.get('area')

    df = pd.read_csv("Crime2025.csv")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.drop(columns=['Total'], errors='ignore')
    melted = df.melt(id_vars=["Crime Classes"], var_name="Area", value_name="Count")
    melted = melted[melted["Count"] > 0]

    # Filter for the selected area
    filtered = melted[melted["Area"] == selected_area]

    pie_data = filtered.groupby("Crime Classes")["Count"].sum().reset_index()
    rows = [[row["Crime Classes"], int(row["Count"])] for _, row in pie_data.iterrows()]

    return jsonify(rows)

if __name__ == "__main__":
    print("🚀 Starting Flask...")
    app.run(debug=True, port=5000)
