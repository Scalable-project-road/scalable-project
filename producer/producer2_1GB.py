import boto3
import json
import random
import requests
import time
import uuid

from datetime import datetime, timezone

# ==========================================================
# AWS CONFIGURATION
# ==========================================================

REGION = "us-east-1"

BATCH_STREAM = "luas-stream"
SPEED_STREAM = "luas-speed-stream"

BUCKET_NAME = "lambda-batch-data"
RAW_PREFIX = "raw"

BATCH_SIZE = 500

TARGET_SIZE = 1024 * 1024 * 1024      # 1 GiB

PRINT_EVERY = 10000

# ==========================================================
# AWS CLIENTS
# ==========================================================

kinesis = boto3.client("kinesis", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)

# ==========================================================
# DATASET
# ==========================================================

CSO_ENDPOINT_URL = (
    "https://ws.cso.ie/public/api.restful/"
    "PxStat.Data.Cube_API.ReadDataset/"
    "TII03/JSON-stat/1.0/en"
)

# ==========================================================
# SYNTHETIC DATA
# ==========================================================

TRAM_IDS = [
    "TRAM-01", "TRAM-02", "TRAM-03", "TRAM-04",
    "TRAM-05", "TRAM-06", "TRAM-07", "TRAM-08",
    "TRAM-09", "TRAM-10", "TRAM-11", "TRAM-12"
]

RED_LINE_STOPS = [
    "Tallaght", "Hospital", "Cookstown", "Belgard", "Kingswood",
    "Red Cow", "Kylemore", "Bluebell", "Blackhorse", "Drimnagh",
    "Goldenbridge", "Suir Road", "Rialto", "Fatima", "James's",
    "Heuston", "Museum", "Smithfield", "Four Courts", "Jervis",
    "Abbey Street", "Busaras", "Connolly", "George's Dock",
    "Mayor Square", "Spencer Dock", "The Point"
]

GREEN_LINE_STOPS = [
    "Bride's Glen", "Cherrywood", "Laughanstown", "Carrickmines",
    "Ballyogan Wood", "Leopardstown Valley", "The Gallops", "Glencairn",
    "Central Park", "Sandyford", "Stillorgan", "Kilmacud", "Dundrum",
    "Balally", "Milltown", "Ranelagh", "Charlemont", "Harcourt",
    "St. Stephen's Green", "Dominick", "Broadstone", "Cabra", "Broombridge"
]

DIRECTIONS = ["Inbound", "Outbound"]

WEATHER = ["Sunny", "Cloudy", "Rain", "Fog", "Windy"]

SERVICE_STATUS = ["On Time", "Minor Delay", "Delayed"]

# ==========================================================
# GENERATE SYNTHETIC EVENT
# ==========================================================

def generate_event(week, line, journeys):

    if "Red" in line:
        stop = random.choice(RED_LINE_STOPS)
    else:
        stop = random.choice(GREEN_LINE_STOPS)

    event = {
        "journey_id": str(uuid.uuid4()),
        "tram_id": random.choice(TRAM_IDS),
        "driver_id": f"DRV-{random.randint(1000, 9999)}",
        "week": week,
        "line": line,
        "stop": stop,
        "direction": random.choice(DIRECTIONS),
        "speed_kmh": random.randint(20, 70),
        "occupancy_percent": random.randint(10, 100),
        "temperature_c": round(random.uniform(5, 25), 1),
        "weather": random.choice(WEATHER),
        "service_status": random.choice(SERVICE_STATUS),
        "delay_seconds": random.randint(0, 300),
        "passenger_journeys": journeys,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return event

# ==========================================================
# UPLOAD BATCH TO S3
# ==========================================================

def upload_batch(batch, batch_number, generated_bytes):

    if len(batch) == 0:
        return

    current_mb = generated_bytes / (1024 * 1024)
    current_gb = generated_bytes / (1024 * 1024 * 1024)

    filename = f"{RAW_PREFIX}/batch_{batch_number:06d}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=filename,
        Body=json.dumps(batch),
        ContentType="application/json"
    )

    print("=" * 70)
    print(f"Batch Uploaded   : {batch_number}")
    print(f"Records in Batch : {len(batch)}")
    print(f"Cumulative Size  : {current_mb:.2f} MB ({current_gb:.3f} GB)")
    print(f"S3 File          : s3://{BUCKET_NAME}/{filename}")
    print("=" * 70)

# ==========================================================
# MAIN PRODUCER
# ==========================================================

def start_luas_stream():

    print("=" * 60)
    print("Downloading CSO dataset...")
    print("=" * 60)

    response = requests.get(CSO_ENDPOINT_URL)
    response.raise_for_status()

    json_data = response.json()
    dataset = json_data["dataset"]

    weeks = list(
        dataset["dimension"]["TLIST(W1)"]["category"]["label"].values()
    )

    lines = list(
        dataset["dimension"]["C03132V03784"]["category"]["label"].values()
    )

    values = dataset["value"]

    print(f"Loaded {len(values)} journey values")

    batch = []
    batch_number = 3226
    generated_records = 0
    generated_bytes = 0
    start_time = time.time()

    while generated_bytes < TARGET_SIZE:

        idx = 0

        for week in weeks:
            for line in lines:

                if line == "All Luas lines":
                    idx += 1
                    continue

                journeys = values[idx]

                if journeys is None:
                    journeys = 0
                else:
                    journeys = int(journeys)

                payload = generate_event(week, line, journeys)

                json_payload = json.dumps(payload)

                record_size = len(json_payload.encode("utf-8"))

                # Send to Batch Stream
                kinesis.put_record(
                    StreamName=BATCH_STREAM,
                    Data=json_payload,
                    PartitionKey=payload["line"]
                )

                # Send to Speed Stream
                kinesis.put_record(
                    StreamName=SPEED_STREAM,
                    Data=json_payload,
                    PartitionKey=payload["line"]
                )

                # Save record for S3 upload
                batch.append(payload)

                generated_records += 1
                generated_bytes += record_size

                # Upload every 500 records
                if len(batch) >= BATCH_SIZE:
                    upload_batch(batch, batch_number, generated_bytes)
                    batch_number += 1
                    batch.clear()

                # Progress Display
                if generated_records % PRINT_EVERY == 0:
                    elapsed = time.time() - start_time
                    print("=" * 60)
                    print(f"Records   : {generated_records:,}")
                    print(f"Generated : {generated_bytes / 1024 / 1024:.2f} MB")
                    print(f"Elapsed   : {elapsed:.1f} seconds")
                    print("=" * 60)

                # Stop at 1 GB
                if generated_bytes >= TARGET_SIZE:
                    if batch:
                        upload_batch(batch, batch_number, generated_bytes)

                    print()
                    print("=" * 60)
                    print("TARGET SIZE REACHED")
                    print(f"Records   : {generated_records:,}")
                    print(f"Generated : {generated_bytes / 1024 / 1024 / 1024:.2f} GB")
                    print("=" * 60)

                    return

                idx += 1
                time.sleep(0.001)

        # Upload remaining records after each dataset cycle
        if batch:
            upload_batch(batch, batch_number, generated_bytes)
            batch_number += 1
            batch.clear()

# ==========================================================
# START PROGRAM
# ==========================================================

if __name__ == "__main__":

    try:
        start_luas_stream()

    except KeyboardInterrupt:
        print("\nProducer stopped.")

    except Exception as e:
        print(f"\nERROR: {e}")
