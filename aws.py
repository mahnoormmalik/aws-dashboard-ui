import boto3 as boto
import boto3
from botocore.exceptions import ClientError
from boto3.session import Session
from datetime import datetime, timedelta

#enter key details here
ACCESS_KEY = ""
SECRET_KEY = ""
AWS_REGION = "eu-north-1"
AMI_ID = ''

S3_CLIENT = boto.client('s3',
                            AWS_REGION,
                            aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
EC2_INSTANCE = boto.client('ec2',
                            AWS_REGION,
                            aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
INSTANCE_ID = ""
SECURITY_GROUP = ""
KEY_PAIR = ""

def launch_ec2_instance(instanceName, ImageID):
    # Python Program for creating a connection

    ec2 = boto.client('ec2',
                      AWS_REGION,
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    # Function for running instances
    conn = ec2.run_instances(InstanceType="t3.micro",
                             MaxCount=1,
                             MinCount=1,
                             ImageId=ImageID,
                             TagSpecifications=[
                                {
                                    'ResourceType': 'instance',
                                    'Tags': [
                                        {
                                            'Key': 'Name',
                                            'Value': instanceName
                                        },
                                    ]
                                },
                            ]
                             )

def reboot_instance(INSTANCE_ID):
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
        return "202"
    except ClientError as e:
        print('Error', e)

def monitor_EC2_Instance():

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
                'Value': "i-0e2cb136d89618d57"
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
    # labels = []
    data = []
    for k, v in response.items():
        if k == 'Datapoints':
            for datapoint in v:
                timeStamp = datapoint["Timestamp"].strftime("%m-%d-%Y %H:%M")
                CPU = datapoint["Average"]
                print(timeStamp, CPU)
                data.append({"timeStamp": timeStamp, "avgCPU" : CPU, "minCPU": datapoint["Minimum"],
                "maxCPU": datapoint["Maximum"]})
    data.sort(key=lambda x: x["timeStamp"])
    return data

def start_instance(EC2_INSTANCE, INSTANCE_ID):

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

def describe_s3_buckets():
    response = S3_CLIENT.list_buckets()

    # Output the bucket names
    buckets = []
    print('Existing buckets:')
    for bucket in response['Buckets']:
        buckets.append({"name": bucket["Name"], "creation_date": bucket["CreationDate"]})
        # print(f'  {bucket["Name"]}')
    
    return buckets

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
        NAME = ""
        if tags: 
            for pair in tags:
                if pair and pair["Key"] == "Name":
                    NAME = pair["Value"]
        # print(NAME)
        INSTANCE_ID = instance.get('Instances')[0].get('InstanceId')
        # print(INSTANCE_ID)

        PUBLIC_DNS_NAME = instance.get('Instances')[0].get('PublicDnsName')
        # print(PUBLIC_DNS_NAME)

        VPC_NAME = instance.get('Instances')[0].get('VpcId')
        # print(VPC_NAME)

        VPC_STATUS = instance.get('Instances')[0].get('State').get('Name')
        # print(VPC_STATUS)

        instances.append({"name": NAME, "instanceID" : INSTANCE_ID, "region": REGION_NAME, "publicDNS": PUBLIC_DNS_NAME, "status": VPC_STATUS})
    instances.sort(key=lambda x: x["status"])
    return instances

def describe_images():
    imageIDs = []
    for image in EC2_INSTANCE.describe_images(Owners=['self'])["Images"]:
        imageIDs.append(image["ImageId"])
    
    return imageIDs

if __name__=="__main__":
    monitor_EC2_Instance()