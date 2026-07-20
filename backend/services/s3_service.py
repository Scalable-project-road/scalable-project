import boto3

import json
 
s3 = boto3.client("s3")
 
BUCKET = "lambda-batch-data"

PREFIX = "processed/"
 
 
def get_latest_batch_result():
 
    response = s3.list_objects_v2(

        Bucket=BUCKET,

        Prefix=PREFIX

    )
 
    json_files = [

        obj for obj in response.get("Contents", [])

        if obj["Key"].endswith(".json")

    ]
 
    if not json_files:

        return {"error": "No JSON files found"}
 
    latest = max(json_files, key=lambda x: x["LastModified"])
 
    obj = s3.get_object(

        Bucket=BUCKET,

        Key=latest["Key"]

    )
 
    content = obj["Body"].read().decode("utf-8").strip()
 
    results = []
 
    for line in content.splitlines():

        if line.strip():

            results.append(json.loads(line))
 
    return results
 
