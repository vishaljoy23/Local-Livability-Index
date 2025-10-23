import json
from google.maps import areainsights_v1
from google.maps.areainsights_v1.types import (
    ComputeInsightsRequest,
    Filter,
    LocationFilter,
    TypeFilter,
    Insight
)
from google.type import latlng_pb2
from google.oauth2 import service_account

CONFIG_FILE = r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json"

def get_area_insights():
    # Initialize the client with service account
    credentials = service_account.Credentials.from_service_account_file(
        r'C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Google Maps\Keys and Auths\maps-api-468005-d9d470437219.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    
    client = areainsights_v1.AreaInsightsClient(
        credentials=credentials
    )

    # Define place types with their radii
    place_types_with_radius = {
        "supermarket": 1000,
        "store": 300,
        "park": 1000,
        "playground": 1000,
        "hospital": 1000,
        "school": 1000,
        "library": 5000,  # 5 km radius
        "police":3500
    }

    # Base location (example: BLR_001)
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    lat = config["City_Details"]["latitude"]
    lon = config["City_Details"]["longitude"]

    amenities_counts = {}

    for place_type, radius in place_types_with_radius.items():
        print(f"\nFetching insights for {place_type} within {radius/1000} km radius...")

        # Create location filter
        location_filter = LocationFilter(
            circle=LocationFilter.Circle(
                lat_lng=latlng_pb2.LatLng(latitude=lat, longitude=lon),
                radius=radius
            )
        )

        # Create type filter
        type_filter = TypeFilter(
            included_primary_types=[place_type]
        )

        # Create the main filter
        filter = Filter(
            location_filter=location_filter,
            type_filter=type_filter
        )

        # Create the request
        request = ComputeInsightsRequest(
            insights=[
                Insight.INSIGHT_COUNT
            ],
            filter=filter
        )

        try:
            # Make the request
            response = client.compute_insights(request=request)
            count = response.count if response.count is not None else 0
            print(f"Total count for {place_type}: {count}")

            amenities_counts[place_type] = count

        except Exception as e:
            print(f"Error occurred for {place_type}: {e}")
            amenities_counts[place_type] = 0  # default to 0 if error

    # Build final JSON structure
    results = {
            "lat": lat,
            "lon": lon,
            "amenities": amenities_counts
    }

    # Save to file
    output_file = "area_insights.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    get_area_insights()
