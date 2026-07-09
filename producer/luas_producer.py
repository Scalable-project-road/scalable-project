import boto3
import json
import time
import requests

# 1. Connect to AWS Kinesis
# (Ensure your AWS Academy Learner Lab is active!)
kinesis_client = boto3.client('kinesis', region_name='us-east-1')

STREAM_NAME = "luas-stream"

# Your exact JSON-stat endpoint
CSO_ENDPOINT_URL = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/TII03/JSON-stat/1.0/en"

def start_luas_stream_from_json_stat():
    try:
        print("Connecting to CSO JSON-stat Endpoint...")
        response = requests.get(CSO_ENDPOINT_URL)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status Code: {response.status_code}")
            return
            
        print("Data downloaded successfully! Parsing JSON-stat format...")
        
        # Parse the JSON-stat data structure
        json_data = response.json()
        print(json_data.keys())
        dataset = json_data["dataset"]
        print("Dataset keys:", dataset.keys())
        print("Dimensions:", dataset["dimension"].keys())
        
        # Extract categories (Weeks and Luas Lines) and the list of passenger numbers (value)
        weeks = dataset["dimension"]["TLIST(W1)"]["category"]["label"]
        weeks_list = list(weeks.values())  # e.g., ["2019 Week 01", "2019 Week 02", ...]
        
        lines = dataset["dimension"]["C03132V03784"]["category"]["label"]
        lines_list = list(lines.values())  # e.g., ["All Luas lines", "Red line", "Green line"]
        
        values = dataset["value"] # Flat list of all passenger totals
        
        print(f"Found {len(values)} records. Simulating live real-time stream...")
        print("Press Ctrl+C to stop.")

        # JSON-stat flattens values by loops. In this dataset order:
        # Loop 1: Weeks, Loop 2: Luas Lines
        idx = 0
        for week in weeks_list:
            for line in lines_list:
                # Skip 'All Luas lines' totals to focus on individual Red/Green lines
                if line == 'All Luas lines':
                    idx += 1
                    continue
                
                # Fetch the individual passenger value (if null/None, default to 0)
                passenger_journeys = values[idx]
                if passenger_journeys is None:
                    passenger_journeys = 0
                else:
                    passenger_journeys = int(passenger_journeys)
                
                # Build the perfect payload for your Kinesis pipeline
                payload = {
                    "statistic": "Passenger Journeys",
                    "week": str(week),
                    "line": str(line),
                    "passenger_journeys": passenger_journeys
                }
                
                # Convert python dictionary to JSON string
                json_payload = json.dumps(payload)
                
                # Push row into your Kinesis Live Stream
                kinesis_client.put_record(
                    StreamName=STREAM_NAME,
                    Data=json_payload,
                    PartitionKey=payload['line']
                )
                
                print(f"Streaming -> {payload['week']} | {payload['line']} | Journeys: {payload['passenger_journeys']}")
                
                # Move to the next index item and sleep to simulate a live data feed
                idx += 1
                time.sleep(0.5)
                
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    start_luas_stream_from_json_stat()
