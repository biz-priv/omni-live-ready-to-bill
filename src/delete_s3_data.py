# """
# * File: src\delete_s3_data.py
# * Project: Omni-live-ready-to-bill
# * Author: Bizcloud Experts
# * Date: 2024-03-15
# * Confidential and Proprietary
# """
import boto3
from datetime import datetime, timedelta, timezone

def lambda_handler(event, context):
    print("event:", event)
    # Initialize the S3 client
    s3 = boto3.client('s3')

    # Specify the source bucket name
    source_bucket = 'dms-dw-etl-lvlp'

    # List of folder names you want to process
    folders_to_process = ['orders', 'movement', 'movement_order', 'stop']

    try:
        # Calculate the timestamp 200 hours ago
        threshold_time = datetime.now(timezone.utc) - timedelta(hours=200)

        # Iterate through the folders
        for folder_name in folders_to_process:
            # Construct the full object key for the folder
            prefix = f"lvlp/prod/dbo/{folder_name}/"
            print("prefix", prefix)

            # Initialize the continuation token
            continuation_token = None

            # Loop to handle pagination
            while True:
                # List objects in the source bucket with the specified prefix
                if continuation_token:
                    response = s3.list_objects_v2(Bucket=source_bucket, Prefix=prefix, ContinuationToken=continuation_token)
                else:
                    response = s3.list_objects_v2(Bucket=source_bucket, Prefix=prefix)

                # Delete objects within the folder
                for obj in response.get('Contents', []):
                    obj_key = obj['Key']
                    last_modified = obj['LastModified']

                    # Check if the object's last modified time is more than 200 hours ago
                    if last_modified < threshold_time:
                        # Delete the object from the source bucket
                        s3.delete_object(Bucket=source_bucket, Key=obj_key)

                # Check if there are more results to fetch
                if response.get('NextContinuationToken'):
                    continuation_token = response['NextContinuationToken']
                else:
                    break  # Exit the loop if there are no more results

        return {
            'statusCode': 200,
            'body': 'Files deleted successfully'
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': 'Error deleting files'
        }
