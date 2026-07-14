import json

import time

import requests

import boto3
 
from google.transit import gtfs_realtime_pb2
 
# -----------------------------

# Configuration

# -----------------------------
 
API_KEY = "339f2d300f51462e9f7508a2e0f3f518"
 
GTFS_URL = "https://api.nationaltransport.ie/gtfsr/v2/vehicles"
 
REGION = "us-east-1"
 
STREAM_NAME = "luas-stream"
 
# -----------------------------

# AWS

# -----------------------------
 
kinesis = boto3.client(

    "kinesis",

    region_name=REGION

)
 
headers = {

    "x-api-key": API_KEY

}
 
print("=" * 60)

print("TFI GTFS Producer Started")

print("=" * 60)
 
while True:
 
    try:
 
        response = requests.get(

            GTFS_URL,

            headers=headers,

            timeout=30

        )
 
        if response.status_code != 200:
 
            print(

                "API Error:",

                response.status_code,

                response.text

            )
 
            time.sleep(5)
 
            continue
 
        feed = gtfs_realtime_pb2.FeedMessage()
 
        feed.ParseFromString(response.content)
 
        print(

            f"\nDownloaded {len(feed.entity)} vehicle records"

        )
 
        sent = 0
 
        for entity in feed.entity:
 
            if not entity.HasField("vehicle"):
 
                continue
 
            vehicle = entity.vehicle
 
            data = {
 
                "vehicle_id":

                    vehicle.vehicle.id

                    if vehicle.vehicle.id else "",
 
                "trip_id":

                    vehicle.trip.trip_id

                    if vehicle.trip.trip_id else "",
 
                "route_id":

                    vehicle.trip.route_id

                    if vehicle.trip.route_id else "",
 
                "latitude":

                    vehicle.position.latitude,
 
                "longitude":

                    vehicle.position.longitude,
 
                "bearing":

                    vehicle.position.bearing,
 
                "speed":

                    vehicle.position.speed,
 
                "timestamp":

                    int(vehicle.timestamp)

                    if vehicle.timestamp else 0
 
            }
 
            kinesis.put_record(
 
                StreamName=STREAM_NAME,
 
                Data=json.dumps(data),
 
                PartitionKey=data["vehicle_id"] or "vehicle"
 
            )
 
            sent += 1
 
        print(

            f"Sent {sent} records to Kinesis"

        )
 
        time.sleep(10)
 
    except Exception as e:
 
        print("Error:", e)
 
        time.sleep(5)
 
