import boto3
import time
import json

def lambda_handler(event, context):
    print(f"Event: {event}")
    record = json.loads(event["Records"][0]["Sns"]["Message"])["Records"][0]
    if (record["eventName"] == "ObjectCreated:Put") \
            and (record["s3"]["bucket"]["name"] =="vnstockmarket-sample-dev") \
            and ("stg_vnindex_historical_index/" in record["s3"]["object"]["key"]):
        client = boto3.client('glue')
        workflow_name = "vnindex_historical_index_workflow"
        response = client.start_workflow_run(
            Name=workflow_name,
        )
        print(response)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"The Glue workflow {workflow_name} has been started!",
            }),
        }




