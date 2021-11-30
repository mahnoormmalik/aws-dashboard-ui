"""
Flask dashboard to manage ec2 instance and list s3 storage

Author: Mahnoor Malik & Tariq Qazzaz
"""

from flask import Flask
from app import app
from aws import describe_s3_buckets, describe_ec2_instance, stop_instance, start_instance, reboot_instance, EC2_INSTANCE, monitor_EC2_Instance,describe_images, launch_ec2_instance
from flask import flash, session, render_template, request, redirect, url_for

#main url of the dashboard. Lists EC2_instance details
@app.route('/')
def index():
    instances = describe_ec2_instance(EC2_INSTANCE)
    return render_template("ui-table.html", instances=instances)

@app.route("/create-instance", methods=['POST'])
def create_instance():
    name = request.form['name']
    amiID = request.form['ami-id']

    if name and amiID:
        launch_ec2_instance(name, amiID)
    return redirect(url_for('index'))


@app.route("/reboot", methods=['POST'])
def reboot():
    instance_id = request.form['id']
    try:
        reboot_instance(instance_id)
    except Exception as e:
        print(e)
    instances = describe_ec2_instance(EC2_INSTANCE)
    return redirect(url_for('index'))

@app.route("/start", methods=['POST'])
def start():
    instance_id = request.form['id']
    try:
        start_instance(EC2_INSTANCE, instance_id)
    except Exception as e:
        print(e)
    instances = describe_ec2_instance(EC2_INSTANCE)
    return redirect(url_for('index'))

@app.route("/stop", methods=['POST'])
def stop():
    instance_id = request.form['id']
    # print(instance_id)
    try:
        stop_instance(EC2_INSTANCE, instance_id)
    except Exception as e:
        print(e)
    instances = describe_ec2_instance(EC2_INSTANCE)
    return redirect(url_for('index'))

@app.route("/s3-dashboard")
def s3_dashboard():
    buckets = describe_s3_buckets()
    # print(buckets)
    return render_template("/home/s3-dashboard.html", buckets=buckets)



@app.route("/add-instance")
def add_instance():
    images = describe_images()
    return render_template("/home/ui-add-instance.html", images=images)

@app.route("/monitor-instance")
def monitor():
    data = monitor_EC2_Instance()

    labels = [row["timeStamp"] for row in data]
    avgCPU = [row["avgCPU"] for row in data]
    minCPU = [row["minCPU"] for row in data]
    maxCPU = [row["maxCPU"] for row in data]

    return render_template("metrics_chart.html", labels=labels, avgCPU=avgCPU, minCPU=minCPU, maxCPU=maxCPU)
if __name__ == "__main__":
    
    app.run(port=5001)