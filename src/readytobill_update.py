import json
import csv 
import boto3
import time
import os
import requests

def lambda_handler(event, context):
    print("event:",event)   
    for item in event["Payload"]:
        order_id=item['item']["order_id"]
        data=get_order(order_id)
        data['ready_to_bill']=True
        response=update_order(data)
        # Update status based on response
        if response == 200:
            status = 'Accepted'
        else:
            status = 'Rejected'
        # Store data in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['Dynamo_Table'])
        table.put_item(
            Item={
                'order_id': order_id,
                'ready_to_bill': response,
                'status': status
            }
                )
        
    return {
        'statusCode': 200,
        'body': json.dumps('Succeeded')
    }

def get_order(order_id):
    username = "apiuser"
    password = "lvlpapiuser"
    mcleod_headers = {'Accept': 'application/json',
                      'Content-type': 'application/json'}
    #url = f'https://tms-lvlp.loadtracking.com:6790/ws/orders/{order_id}'
    url = f'https://tms-lvlp.loadtracking.com/ws/orders/{order_id}'
    response = requests.get(url, auth=(username, password), headers=mcleod_headers)
    output = response.json()
    if(response.status_code==200):
        return output
    else:
        print("order_id",response.status_code)

def update_order(json_data):
    username = "apiuser"
    password = "lvlpapiuser"
    mcleod_headers = {'Accept': 'application/json',
                      'Content-type': 'application/json'}
    
    print("json",json_data)
    url = os.environ['url']
    response = requests.put(url, auth=(username, password), headers=mcleod_headers,json=json_data)
    print("response ",response.text)
    output = response.json()
    return response.status_code