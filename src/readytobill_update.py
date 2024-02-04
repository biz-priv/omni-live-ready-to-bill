import json
import csv 
import boto3
import time
import os
import requests

def lambda_handler(event, context):
    print("event:",event)
    return
    
    s3 = boto3.client('s3')

    s3_bucket = s3_file_path.split('/', 3)[-2]
    s3_key = s3_file_path.split('/', 3)[-1]
    response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    csv_content = response['Body'].read().decode('utf-8')
    reader = csv.reader(csv_content.splitlines())
    rows = [row for row in reader]
    if len(rows) > 1:
        data_rows = rows[1:]  # Exclude header row
        print("Data:", data_rows)
    else:
        print("No data found in the CSV.")
    
    ready_to_bill = True
    for order in data_rows:
        order_id=order[0]
        shipper_stop_id=order[5]
        consignee_stop_id=order[6]
        response=update_order(order_id,shipper_stop_id,consignee_stop_id)
        # Update status based on response
        if response == 200:
            status = 'Accepted'
        elif response in [400, 401,405]:
            status = 'Rejected'

        # Store data in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['Dynamo_Table'])
        table.put_item(
            Item={
                'order_id': order_id,
                'ready_to_bill': ready_to_bill,
                'status': status
            }
                )
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def update_order(id,shipper_stop_id,consignee_stop_id):
    username = "apiuser"
    password = "lvlpapiuser"
    mcleod_headers = {'Accept': 'application/json',
                      'Content-type': 'application/json'}
    json_data={
    "__type": "orders",
    "company_id": "TMS",
    "id": id,
    "ready_to_bill": True,
    "stops": [
        {
            "__type": "stop",
            "__name": "stops",
            "company_id": "TMS",
            "id": shipper_stop_id
        },
        {
            "__type": "stop",
            "__name": "stops",
            "company_id": "TMS",
            "id": consignee_stop_id
        }
            ]
        }
    print("json",json_data)
    url = f'https://tms-lvlp.loadtracking.com:6790/ws/api/orders/update'
    response = requests.put(url, auth=(username, password), headers=mcleod_headers,json=json_data)
    print("response",response.text)
    output = response.json()
    return response.status_code