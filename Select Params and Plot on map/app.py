from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)
CORS(app)  # allow requests from your HTML page

# -------------------------------------
# Load dataset
# -------------------------------------
df = pd.read_csv("livability_data.csv")

# -------------------------------------
# Define weights
# -------------------------------------
weights = {
    'aqi': 10, 'wqi': 7, 'park': 4, 'playground': 4,
    'hospital': 6, 'school': 5, 'supermarket': 3, 'store': 2, 'library': 4,
    'congestion': 9, 'local_congestion': 6,
    'sqft_price': 10, 'hdi_rank': 5,
    'voter_turnout': 10
}

negative_params = ['aqi', 'congestion', 'local_congestion', 'sqft_price', 'hdi_rank']

# -------------------------------------
# Helper function: compute score
# -------------------------------------
def compute_livability(selected_params):
    # Validate
    selected_params = [p for p in selected_params if p in weights]
    if not selected_params:
        return None, "No valid parameters selected."

    df_norm = df.copy()
    scaler = MinMaxScaler()
    df_norm[selected_params] = scaler.fit_transform(df[selected_params])

    # Flip negative-impact indicators
    for col in selected_params:
        if col in negative_params:
            df_norm[col] = 1 - df_norm[col]

    # Compute weighted livability score
    total_weight = sum(weights[p] for p in selected_params)
    df_norm['selectedParamsScore'] = sum(df_norm[p] * weights[p] for p in selected_params)
    df_norm['selectedParamsScore'] = (df_norm['selectedParamsScore'] / total_weight) * 100

    # Save CSV with selected columns
    csv_path = "selectedParams.csv"
    df_norm[['city', 'area', 'latitude', 'longitude', 'selectedParamsScore']].to_csv(csv_path, index=False)

    # --- Generate Folium Map ---
    import folium
    from branca.colormap import linear

    OUTPUT = "mapBLRHYD.html"
    df_map = df_norm[['city', 'area', 'latitude', 'longitude', 'selectedParamsScore']].copy()
    df_map_sorted = df_map.sort_values(by="selectedParamsScore", ascending=True)

    m = folium.Map(
        location=[df_map["latitude"].mean(), df_map["longitude"].mean()],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    colormap = linear.RdYlGn_11.scale(0, 100)
    colormap.caption = 'Score (0 = Low, 100 = High)'
    colormap.add_to(m)

    min_score, max_score = df_map["selectedParamsScore"].min(), df_map["selectedParamsScore"].max()

    for _, row in df_map_sorted.iterrows():
        score = row["selectedParamsScore"]
        area = row["area"]
        norm = (score - min_score) / (max_score - min_score + 1e-9)
        radius = 4 + 9 * norm           # 4–13 px radius
        opacity = 0.2 + 0.8 * norm      # 0.2–1 opacity

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color=colormap(score),
            fill=True,
            fill_color=colormap(score),
            fill_opacity=opacity,
            tooltip=f"<b>Area:</b> {area}<br><b>Score:</b> {score:.2f}",
        ).add_to(m)

    m.save(OUTPUT)
    print(f"Map saved to {OUTPUT} (open in browser)")

    # Return top areas for frontend
    result = df_norm[['city', 'area', 'selectedParamsScore']].sort_values(by='selectedParamsScore', ascending=False)
    return result, None


# -------------------------------------
# Route: Compute livability score
# -------------------------------------
@app.route("/compute", methods=["POST"])
def compute():
    data = request.get_json()
    selected_params = data.get("parameters", [])
    
    result, error = compute_livability(selected_params)
    if error:
        return jsonify({"error": error}), 400

    # Convert top 10 to JSON
    top10 = result.head(10).to_dict(orient='records')
    return jsonify({
        "selected_parameters": selected_params,
        "top_areas": top10
    })

# -------------------------------------
# Run the app
# -------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
