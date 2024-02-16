import boto3
import time
import pandas as pd
import requests
import json
import awswrangler as wr

def lambda_handler(event, context):

    client = boto3.client('ecs')

    cluster_name = 'web_scraping_api_demo'
    task_family = 'run_web_scraping_api_demo'
    subnet1 = 'subnet-0d4eda1f233c858c2'
    subnet2 = 'subnet-0ea9853bd0f5d3e88'
    subnet3 = 'subnet-0b1c8cd53b0da8492'
    securityGroup = 'sg-0374225503e692273'

    s3_bucket = 'vnstockmarket-sample-dev'
    sub_path = 'stg_vnindex_historical_index/'

    response = client.run_task(
        cluster=cluster_name,
        taskDefinition=task_family,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    subnet1,
                    subnet2,
                    subnet3,
                ],
                'securityGroups': [
                    securityGroup,
                ],
                'assignPublicIp': 'ENABLED'
            }
        }
    )

    task_arn = response['tasks'][0]['containers'][0]['taskArn']
    print(task_arn)
    time.sleep(60)
    response = client.describe_tasks(
        cluster=cluster_name,
        tasks=[
            task_arn,
        ],
    )
    private_ip = response['tasks'][0]['containers'][0]['networkInterfaces'][0]['privateIpv4Address']
    eni_id = None
    for detail in response['tasks'][0]['attachments'][0]['details']:
        if 'eni-' in detail['value']:
            eni_id = detail['value']

    eni = boto3.resource('ec2').NetworkInterface(eni_id)
    public_ip = eni.association_attribute['PublicIp']
    print(private_ip, eni_id, public_ip)

    BASE = f"http://{public_ip}:5000/"

    response = requests.get(BASE + 'data')
    response = json.loads(response.json())
    df = pd.DataFrame(response)
    print(df)
    filename = df['RECORDED_DATE'].values[0]
    filename = filename.split("/")
    filename = [filename[len(filename) - i - 1] for i in range(len(filename))]
    filename = ''.join(filename)
    destination = f"s3://{s3_bucket}/{sub_path}{filename}.csv"
    print(destination)
    wr.s3.to_csv(df, destination, index=False)

    # Stop ECS task
    client.stop_task(
        cluster=cluster_name,
        task=task_arn,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "The today VNINDEX has been stored in S3!",
        }),
    }


