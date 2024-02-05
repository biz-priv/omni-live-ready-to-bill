import json
import csv 
import boto3
import time
import os
import requests

def lambda_handler(event, context):
    print("event:",event)    
    ready_to_bill = True
    for item in event["Payload"]:
        order_id=item['item']["order_id"]
        shipper_stop_id=item['item']["shipper_stop_id"]
        consignee_stop_id=item['item']["consignee_stop_id"]
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
    url = os.environ['url']
    response = requests.put(url, auth=(username, password), headers=mcleod_headers,json=json_data)
    print("response",response.text)
    output = response.json()
    return response.status_code