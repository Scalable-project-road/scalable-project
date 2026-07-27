import boto3

import json
 
BUCKET_NAME = "lambda-batch-data"

PREFIX = "speed-results/"
 
s3 = boto3.client("s3")
 
 
def get_latest_realtime():

    response = s3.list_objects_v2(

        Bucket=BUCKET_NAME,

        Prefix=PREFIX

    )
 
    if "Contents" not in response:

        return {"message": "No realtime data found"}
 
    latest = max(

        response["Contents"],

        key=lambda x: x["LastModified"]

    )
 
    obj = s3.get_object(

        Bucket=BUCKET_NAME,

        Key=latest["Key"]

    )
 
    data = json.loads(

        obj["Body"].read().decode("utf-8")

    )
 
    return data
 
