import boto3
import os
import json







def lambda_handler(event, context):
    # Define your EC2 configurations
    ec2_client = boto3.client('ec2')
    s3_client = boto3.client('s3')
    route53_client = boto3.client('route53')
    ssm_client = boto3.client('ssm')
    region=os.environ['REGION']
    instance_type=os.environ['INSTANCE_TYPE']
    ami_id=os.environ['AMI']
    key_name=os.environ['KEY_NAME']
    SUBNET_ID=os.environ['SUBNET_ID']
    hosted_zone_id=os.environ['HOSTED_ZONE_ID']
    subdomain=os.environ['SUBDOMAIN']
    instance_name = subdomain.split('.')[0]



    # Step 1: Create EC2 instance
    instance = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1,
        SubnetId=SUBNET_ID,
        TagSpecifications=[{    #This creates a tag for our resource
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name','Value': instance_name}]
        }]  
        # Add other necessary parameters
    )

    instance_id = instance['Instances'][0]['InstanceId']
    
    # Wait for the instance to be running
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    
    # Step 2: Get public IPv4 address
    instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])
    public_ip = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']

    print(f"Public IPv4 address: {public_ip}")

        # Step 3: Update Route 53 record with the public IP
    domain_name1 = f"{subdomain}.ecommerce.phytts.com"
    domain_name2 = f"{subdomain}.erp.phytts.com"
    domain_name3 = f"{subdomain}.saas.phytts.com"
    change_batch = {
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': domain_name1,
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [{'Value': public_ip}],
                }
            }
        ]
    }

    route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=change_batch
    )
    
        # Step 3: Update Route 53 record with the public IP

    change_batch = {
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': domain_name2,
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [{'Value': public_ip}],
                }
            }
        ]
    }

    route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=change_batch
    )
    
        # Step 3: Update Route 53 record with the public IP

    change_batch = {
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': domain_name3,
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [{'Value': public_ip}],
                }
            }
        ]
    }

    route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=change_batch
    )

    print(f"Updated Route 53 record for {subdomain} with IP: {public_ip}")
    
    
   
    return {
        'statusCode': 200,
        'body': json.dumps(f"EC2 instance created, public IP: {public_ip}, and file renamed.")
    }

    
    
    