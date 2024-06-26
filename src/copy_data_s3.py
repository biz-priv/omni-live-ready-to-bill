# """
# * File: src\copy_data_s3.py
# * Project: Omni-live-ready-to-bill
# * Author: Bizcloud Experts
# * Date: 2024-03-15
# * Confidential and Proprietary
# """
import boto3
from datetime import datetime, timedelta,timezone

def lambda_handler(event, context):
    # Initialize the S3 client
    s3 = boto3.client('s3')

    # Specify the source and destination bucket names
    source_bucket = 'dms-dw-etl-lvlp'
    destination_bucket = 'dms-dw-etl-lvlp'

    # List of folder names you want to process
    folders_to_process = ['movement','movement_order','orders','stop']
    # Calculate the time 5 hours ago
    five_hours_ago = datetime.now(timezone.utc) - timedelta(hours=5)

    # Iterate through the folders
    for folder_name in folders_to_process:
        # Construct the full object key for the folder
        prefix = f"prod/dbo/{folder_name}/"
        print("prefix",prefix)

        # Initialize continuation token for pagination
        continuation_token = None

        while True:
            # List objects in the source bucket with the specified prefix and time-based filtering
            if continuation_token:
                response = s3.list_objects_v2(
                    Bucket=source_bucket,
                    Prefix=prefix,
                    ContinuationToken=continuation_token,
                    
                )
            else:
                response = s3.list_objects_v2(
                    Bucket=source_bucket,
                    Prefix=prefix,
                    
                )

            # Copy only the objects that meet the time-based criteria
            for obj in response.get('Contents', []):
                obj_key = obj['Key']
                last_modified_time = obj['LastModified']
                
                # Check if the object was modified within the last 5 hours
                if last_modified_time >= five_hours_ago:
                    # Copy object from source to destination bucket
                    copy_source = {'Bucket': source_bucket, 'Key': obj_key}
                    dest_key = f"lvlp/{obj_key}"  # You can modify the key if needed
                    s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=dest_key)

            # Check if there are more objects to fetch
            if response.get('NextContinuationToken'):
                continuation_token = response['NextContinuationToken']
            else:
                break

    return {
        'statusCode': 200,
        'body': 'Files copied successfully'
    }
