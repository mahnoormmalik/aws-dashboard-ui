import logging
import boto3
from botocore.exceptions import ClientError
from boto3.session import Session
import boto3 as boto
import time
from datetime import date, datetime
import os
import pandas as pd
import sys
from datetime import datetime, timedelta


def create_tags(ACCESS_KEY, SECRET_KEY, region):

    ec2 = boto.client('ec2',
                      region,
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    response = ec2.create_tags(
        Resources=[
            'i-0e870359021e11d97',
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'mt_lab3'
            },
        ]
    )


def launch_ec2_instance(ACCESS_KEY, SECRET_KEY, AWS_REGION):
    # Python Program for creating a connection

    ec2 = boto.client('ec2',
                      AWS_REGION,
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    # Function for running instances
    conn = ec2.run_instances(InstanceType="t3.micro",
                             MaxCount=1,
                             MinCount=1,
                             ImageId="ami-09733597242dc581b",
                             TagSpecifications=[
                                {
                                    'ResourceType': 'instance',
                                    'Tags': [
                                        {
                                            'Key': 'Name',
                                            'Value': 'Mahnoor-lab3'
                                        },
                                    ]
                                },
                            ]
                             )


# This function will describe all the instances
# with their current state


def manage_ec2_instance(ACCESS_KEY, SECRET_KEY, AWS_REGION, EC2_INSTANCE):

    Myec2 = EC2_INSTANCE.describe_instances()
    for instance in Myec2['Reservations']:
        # print(instance)

        # print(instance.get('Instances')[0])
        # if instance.get('Instances')[0].get('InstanceId') == 'i-0e2cb136d89618d57':

        REGION_NAME = instance.get('Instances')[0].get(
            'Placement').get('AvailabilityZone')
        print(REGION_NAME)
        
        INSTANCE_ID = instance.get('Instances')[0].get('InstanceId')
        print(INSTANCE_ID)

        PUBLIC_DNS_NAME = instance.get('Instances')[0].get('PublicDnsName')
        print(PUBLIC_DNS_NAME)

        VPC_NAME = instance.get('Instances')[0].get('VpcId')
        print(VPC_NAME)

        VPC_STATUS = instance.get('Instances')[0].get('State').get('Name')
        print(VPC_STATUS)


def start_instance(EC2_INSTANCE, INSTANCE_ID, SECURITY_GROUP, KEY_PAIR):

    # Do a dryrun first to verify permissions
    try:
        EC2_INSTANCE.start_instances(InstanceIds=[INSTANCE_ID], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise
    try:
        response = EC2_INSTANCE.start_instances(
            InstanceIds=[INSTANCE_ID], DryRun=False)
        print(response)
    except ClientError as e:
        print(e)

    # Dry run succeeded, run start_instances without dryrun


def retrieve_status():
    pass


def stop_instance(EC2_INSTANCE, INSTANCE_ID):
    try:
        EC2_INSTANCE.stop_instances(InstanceIds=[INSTANCE_ID], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    # Dry run succeeded, call stop_instances without dryrun
    try:
        response = EC2_INSTANCE.stop_instances(
            InstanceIds=[INSTANCE_ID], DryRun=False)
        print(response)
    except ClientError as e:
        print(e)


def reboot_instance(EC2_INSTANCE, INSTANCE_ID):
    try:
        EC2_INSTANCE.reboot_instances(InstanceIds=[INSTANCE_ID], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            print("You don't have permission to reboot instances.")
            raise

    try:
        response = EC2_INSTANCE.reboot_instances(
            InstanceIds=[INSTANCE_ID], DryRun=False)
        print('Success', response)
    except ClientError as e:
        print('Error', e)


def monitor_EC2_Instance(AWS_REGION, ACCESS_KEY, SECRET_KEY):

    client = boto3.client('cloudwatch', region_name=AWS_REGION,
                            aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
    time = datetime.utcnow()
    response = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': ""
            },
        ],
        StartTime=time - timedelta(seconds=3600),
        EndTime=time,
        Period=300,
        Statistics=[
            'Average', 'Minimum','Maximum', 
        ],
        Unit='Percent'
    )
    # date_time.strftime("%m/%d/%Y, %H:%M:%S")

    for k, v in response.items():
        if k == 'Datapoints':
            for y in v:
                print(y)
def describe_ec2_instance(EC2_INSTANCE):

    Myec2 = EC2_INSTANCE.describe_instances()
    instances = []

    # print(Myec2["Reservations"])
    for instance in Myec2['Reservations']:
        # print(instance)

        # print(instance.get('Instances')[0])
        # if instance.get('Instances')[0].get('InstanceId') == 'i-0e2cb136d89618d57':

        REGION_NAME = instance.get('Instances')[0].get(
            'Placement').get('AvailabilityZone')
        # print(REGION_NAME)
        tags = instance.get('Instances')[0].get("Tags")
        NAME = None
        if tags: 
            for pair in tags:
                if pair and pair["Key"] == "Name":
                    NAME = pair["Value"]
        print(NAME)
        INSTANCE_ID = instance.get('Instances')[0].get('InstanceId')
        # print(INSTANCE_ID)

        PUBLIC_DNS_NAME = instance.get('Instances')[0].get('PublicDnsName')
        # print(PUBLIC_DNS_NAME)

        VPC_NAME = instance.get('Instances')[0].get('VpcId')
        # print(VPC_NAME)

        VPC_STATUS = instance.get('Instances')[0].get('State').get('Name')
        # print(VPC_STATUS)

        instances.append({"name": NAME, "instanceID" : INSTANCE_ID, "region": REGION_NAME, "publicDNS": PUBLIC_DNS_NAME, "status": VPC_STATUS})

if __name__ == "__main__":

    ACCESS_KEY = ""
    SECRET_KEY = ""
    AWS_REGION = "eu-north-1"
    AMI_ID = 'ami-09733597242dc581b'
    EC2_INSTANCE = boto.client('ec2',
                               AWS_REGION,
                               aws_access_key_id=ACCESS_KEY,
                               aws_secret_access_key=SECRET_KEY)
    INSTANCE_ID = ""
    SECURITY_GROUP = ""
    KEY_PAIR = ""

    # describe_ec2_instance(EC2_INSTANCE)
    # start_instance(EC2_INSTANCE, INSTANCE_ID , SECURITY_GROUP , KEY_PAIR)
    # stop_instance(EC2_INSTANCE, INSTANCE_ID)
    # reboot_instance(EC2_INSTANCE, INSTANCE_ID)
    launch_ec2_instance(ACCESS_KEY, SECRET_KEY, AWS_REGION)
    # create_tags(ACCESS_KEY, SECRET_KEY, region)
    # manage_ec2_instance(ACCESS_KEY, SECRET_KEY, AWS_REGION, EC2_INSTANCE)
    for image in EC2_INSTANCE.describe_images(Owners=['self'])["Images"]:
        print(image["ImageId"])
    # monitor_EC2_Instance(AWS_REGION, ACCESS_KEY, SECRET_KEY)
    # read arguments from the command line and
    # check whether at least two elements were entered
