# Event-Driven File Notification Pipeline (AWS CLI)

A fully serverless, event-driven pipeline built entirely with the AWS CLI. When a file is uploaded to S3, its details (name, size, type, last modified, ETag, storage class) are automatically emailed via SNS.

## Architecture

**Flow:** S3 Upload → SQS Queue → Lambda → S3 (fetch metadata) → SNS → Email

1. A file is uploaded to an S3 bucket
2. A message describing the file (`{"bucket": ..., "key": ...}`) is sent to an SQS queue
3. The SQS to Lambda event source mapping triggers the Lambda function
4. Lambda parses the message, calls `s3:GetObject` to fetch the file's metadata
5. Lambda publishes a formatted notification to an SNS topic
6. SNS delivers the notification by email to the confirmed subscriber

## Key design decisions

- **Least-privilege IAM** — every permission is scoped to one exact resource ARN. No wildcard `Resource` values anywhere.
- **Resilient error handling** — Lambda reports failures per message using SQS batch item failures, so one malformed message doesn't block the rest of the queue.
- **Decoupled architecture** — SQS buffers between the trigger and the processor, so a slow or failing Lambda doesn't lose data; messages simply remain in the queue for retry.

## Repo structure

```
iam/
  trust-policy.json         Trust policy allowing Lambda to assume the role
  permissions-policy.json   Least-privilege permissions (S3, SQS, SNS, CloudWatch Logs)
lambda/
  lambda_function.py        Lambda handler: reads SQS, fetches S3 metadata, publishes to SNS
screenshots/
  (architecture diagram and execution proof added separately)
```

## Notes

- All account-specific values (account ID, bucket name) are replaced with placeholders in the IAM policy files.
- The Lambda function reads the SNS topic ARN from an environment variable (`SNS_TOPIC_ARN`) rather than hardcoding it.
- All AWS resources used in this project were deleted after testing to avoid ongoing charges.

## Built with

Amazon S3, Amazon SQS, AWS Lambda (Python 3.12), Amazon SNS, AWS IAM, Amazon CloudWatch Logs — provisioned entirely via AWS CLI.
