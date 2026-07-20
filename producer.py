import boto3

import json

import time

import requests
 
# =====================================================

# AWS Configuration

# =====================================================
 
REGION = "us-east-1"
 
BATCH_STREAM = "luas-stream"

SPEED_STREAM = "luas-speed-stream"
 
S3_BUCKET = "lambda-batch-data"

S3_PREFIX = "raw"
 
# =====================================================

# AWS Clients

# =====================================================
 
kinesis_client = boto3.client(

    "kinesis",

    region_name=REGION

)
 
s3_client = boto3.client(

    "s3",

    region_name=REGION

)
 
# =====================================================

# Dataset

# =====================================================
 
CSO_ENDPOINT_URL = (

    "https://ws.cso.ie/public/api.restful/"

    "PxStat.Data.Cube_API.ReadDataset/"

    "TII03/JSON-stat/1.0/en"

)
 
# =====================================================

# Producer

# =====================================================
 
def start_luas_stream():
 
    try:
 
        print("=" * 70)

        print("Connecting to CSO JSON-stat API...")

        print("=" * 70)
 
        response = requests.get(CSO_ENDPOINT_URL)
 
        if response.status_code != 200:

            print("Unable to download dataset.")

            return
 
        json_data = response.json()
 
        dataset = json_data["dataset"]
 
        weeks = dataset["dimension"]["TLIST(W1)"]["category"]["label"]

        weeks_list = list(weeks.values())
 
        lines = dataset["dimension"]["C03132V03784"]["category"]["label"]

        lines_list = list(lines.values())
 
        values = dataset["value"]
 
        print(f"Loaded {len(values)} records.")

        print("Streaming continuously...\n")
 
        while True:
 
            idx = 0
 
            print("=" * 70)

            print("Starting New Streaming Cycle")

            print("=" * 70)
 
            for week in weeks_list:
 
                for line in lines_list:
 
                    if line == "All Luas lines":

                        idx += 1

                        continue
 
                    journeys = values[idx]
 
                    if journeys is None:

                        journeys = 0

                    else:

                        journeys = int(journeys)
 
                    payload = {

                        "statistic": "Passenger Journeys",

                        "week": str(week),

                        "line": str(line),

                        "passenger_journeys": journeys,

                        "timestamp": int(time.time())

                    }
 
                    json_payload = json.dumps(payload)
 
                    # ==================================

                    # Send to Batch Kinesis Stream

                    # ==================================
 
                    kinesis_client.put_record(

                        StreamName=BATCH_STREAM,

                        Data=json_payload,

                        PartitionKey=payload["line"]

                    )
 
                    # ==================================

                    # Send to Speed Kinesis Stream

                    # ==================================
 
                    kinesis_client.put_record(

                        StreamName=SPEED_STREAM,

                        Data=json_payload,

                        PartitionKey=payload["line"]

                    )
 
                    # ==================================

                    # Store Raw Record in S3

                    # ==================================
 
                    filename = (

                        f"{S3_PREFIX}/"

                        f"{payload['week']}_"

                        f"{payload['line'].replace(' ','_')}_"

                        f"{payload['timestamp']}.json"

                    )
 
                    s3_client.put_object(

                        Bucket=S3_BUCKET,

                        Key=filename,

                        Body=json_payload,

                        ContentType="application/json"

                    )
 
                    print(

                        f"Week: {payload['week']} | "

                        f"Line: {payload['line']} | "

                        f"Passengers: {payload['passenger_journeys']} | "

                        f"Kinesis ✓ | S3 ✓"

                    )
 
                    idx += 1
 
                    time.sleep(1)
 
            print("\nDataset completed.")

            print("Restarting...\n")
 
            time.sleep(2)
 
    except KeyboardInterrupt:

        print("\nProducer stopped.")
 
    except Exception as e:

        print("Error:", e)
 
 
if __name__ == "__main__":

    start_luas_stream()
 
