import json
import os
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    batch_item_failures = []

    for record in event.get('Records', []):
        message_id = record.get('messageId')
        try:
            body = json.loads(record['body'])
            bucket = body['bucket']
            key = body['key']

            response = s3_client.head_object(Bucket=bucket, Key=key)

            file_size = response.get('ContentLength')
            content_type = response.get('ContentType', 'unknown')
            last_modified = str(response.get('LastModified'))
            etag = response.get('ETag', '').strip('"')
            storage_class = response.get('StorageClass', 'STANDARD')

            message = (
                f"New file uploaded to S3!\n\n"
                f"File Name: {key}\n"
                f"Bucket: {bucket}\n"
                f"Size: {file_size} bytes\n"
                f"Content Type: {content_type}\n"
                f"Last Modified: {last_modified}\n"
                f"ETag: {etag}\n"
                f"Storage Class: {storage_class}\n"
            )

            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"S3 File Notification: {key}",
                Message=message
            )

            print(f"Successfully processed {key} from {bucket}")

        except ClientError as e:
            print(f"AWS error processing message {message_id}: {e}")
            batch_item_failures.append({"itemIdentifier": message_id})
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Invalid message format for {message_id}: {e}")
            batch_item_failures.append({"itemIdentifier": message_id})
        except Exception as e:
            print(f"Unexpected error processing message {message_id}: {e}")
            batch_item_failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": batch_item_failures}
