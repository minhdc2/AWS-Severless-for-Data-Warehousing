import boto3
import time
import json

def lambda_handler(event, context):

    client = boto3.client('rds')
    cluster_id = "aurora-1"

    response = client.describe_db_clusters(
        DBClusterIdentifier=cluster_id
    )
    for cluster in response["DBClusters"]:
        if cluster["DBClusterIdentifier"] == cluster_id:
            status = cluster["Status"]
            if status == "stopped":
                # start aurora cluster
                response = client.start_db_cluster(
                    DBClusterIdentifier=cluster_id
                )
                print(response)

                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "message": f"Aurora Serverless cluster {cluster_id} has been started and stopped!",
                    }),
                }

                break


