from datetime import datetime
from local_congestion import next_weekday 

def test_next_weekday_normal():

    monday = datetime(2026, 9, 21)

    result = next_weekday(monday)

    assert result.weekday() == 1 # Tuesday


def test_next_weekday_skips_weekend():

    friday = datetime(2026, 9, 25)

    result = next_weekday(friday)

    assert result.weekday() == 0
    assert result.day == 28


from geopy.distance import distance
from local_congestion import get_point
import pytest


def test_get_point_distance():

    center = (12.9716, 77.5946)

    result = get_point(center, 1, 90)

    generated_point = (result[0], result[1])

    actual_distance = distance(
        center,
        generated_point
    ).km

    assert actual_distance == pytest.approx(
        1,
        abs=0.01
    )


def test_get_point_preserves_bearing():

    center = (12.9716, 77.5946)

    result = get_point(center, 2, 45)

    assert result[2] == 45


from unittest.mock import patch, Mock
from datetime import datetime

from local_congestion import gmaps_directions


@patch("local_congestion.requests.get")
def test_gmaps_success(mock_get):

    mock_get.return_value.status_code = 200

    mock_get.return_value.json.return_value = {
        "status": "OK",
        "routes": [
            {
                "legs": [
                    {
                        "duration": {
                            "value": 600
                        },
                        "duration_in_traffic": {
                            "value": 900
                        }
                    }
                ]
            }
        ]
    }

    origin = (12.97, 77.59)
    destination = (12.98, 77.60)

    normal, traffic = gmaps_directions(
        origin,
        destination,
        datetime(2026, 9, 28, 18, 0)
    )

    assert normal == 600
    assert traffic == 900

@patch("local_congestion.requests.get")
def test_gmaps_missing_traffic(mock_get):

    mock_get.return_value.status_code = 200

    mock_get.return_value.json.return_value = {
        "status": "OK",
        "routes": [
            {
                "legs": [
                    {
                        "duration": {
                            "value": 600
                        }
                    }
                ]
            }
        ]
    }

    normal, traffic = gmaps_directions(
        (12.97, 77.59),
        (12.98, 77.60),
        datetime(2026, 9, 28, 18)
    )

    assert normal == 600
    assert traffic is None

@patch("local_congestion.time.sleep")
@patch("local_congestion.requests.get")
def test_gmaps_retries(mock_get, mock_sleep):

    failed_response = Mock()
    failed_response.status_code = 500

    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = {
        "status": "OK",
        "routes": [
            {
                "legs": [
                    {
                        "duration": {"value": 600},
                        "duration_in_traffic": {
                            "value": 900
                        }
                    }
                ]
            }
        ]
    }

    mock_get.side_effect = [
        failed_response,
        failed_response,
        success_response
    ]

    normal, traffic = gmaps_directions(
        (12.97, 77.59),
        (12.98, 77.60),
        datetime(2026, 9, 28, 18)
    )

    assert mock_get.call_count == 3

    assert normal == 600
    assert traffic == 900



@patch("local_congestion.time.sleep")
@patch("local_congestion.requests.get")
def test_gmaps_all_retries_fail(
    mock_get,
    mock_sleep
):

    mock_get.return_value.status_code = 500

    normal, traffic = gmaps_directions(
        (12.97, 77.59),
        (12.98, 77.60),
        datetime(2026, 9, 28, 18)
    )

    assert mock_get.call_count == 3

    assert normal is None
    assert traffic is None


from local_congestion import measure_city

@patch("local_congestion.time.sleep")
@patch("local_congestion.gmaps_directions")
def test_measure_city_ratio(
    mock_gmaps,
    mock_sleep
):

    mock_gmaps.return_value = (100, 150)

    results = measure_city("Bengaluru")

    assert len(results) > 0

    assert results[0]["normal_duration_sec"] == 100
    assert results[0]["traffic_duration_sec"] == 150

    assert results[0]["congestion_ratio"] == 1.5










import pandas as pd
from local_congestion import compute_city_congestion_index, save_results

def test_compute_congestion_index(tmp_path):

    csv_file = tmp_path / "traffic.csv"

    data = [
        {
            "city": "Bengaluru",
            "radius_km": 1,
            "bearing_deg": 0,
            "time_label": "freeflow",
            "traffic_duration_sec": 100
        },
        {
            "city": "Bengaluru",
            "radius_km": 1,
            "bearing_deg": 0,
            "time_label": "peak",
            "traffic_duration_sec": 200
        },
        {
            "city": "Bengaluru",
            "radius_km": 2,
            "bearing_deg": 0,
            "time_label": "freeflow",
            "traffic_duration_sec": 100
        },
        {
            "city": "Bengaluru",
            "radius_km": 2,
            "bearing_deg": 0,
            "time_label": "peak",
            "traffic_duration_sec": 150
        }
    ]

    pd.DataFrame(data).to_csv(
        csv_file,
        index=False
    )

    result = compute_city_congestion_index(csv_file)

    index = result[
        "city_congestion_index"
    ].iloc[0]

    assert index == pytest.approx(1.8)




def test_save_results(tmp_path):

    output = tmp_path / "output.csv"

    results = [
        {
            "city": "Bengaluru",
            "radius_km": 1,
            "congestion_ratio": 1.5
        }
    ]

    save_results(results, output)

    df = pd.read_csv(output)

    assert len(df) == 1
    assert df.iloc[0]["city"] == "Bengaluru"
    assert df.iloc[0]["congestion_ratio"] == 1.5