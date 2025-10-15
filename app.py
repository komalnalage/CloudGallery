import boto3
from flask import Flask, render_template, request, redirect
import uuid
from datetime import datetime

app = Flask(__name__)

S3_BUCKET = "cloud-gallery-mini-project"
DYNAMODB_TABLE = "CloudGallery"
AWS_REGION = "ap-south-1"

s3 = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        if file:
            filename = str(uuid.uuid4()) + "_" + file.filename
            s3.upload_fileobj(file, S3_BUCKET, filename)
            table.put_item(Item={
                "id": str(uuid.uuid4()),
                "filename": filename,
                "upload_time": str(datetime.now()),
                "url": f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"

            })
        return redirect("/")

    # GET request - fetch all images from DynamoDB
    response = table.scan()
    images = response.get("Items", [])
    return render_template("index.html", images=images)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
