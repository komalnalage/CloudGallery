from flask import Flask, render_template, request, redirect
import boto3
import uuid
from datetime import datetime

app = Flask(__name__)

# AWS Config
S3_BUCKET = "your-s3-bucket-name"
DYNAMODB_TABLE = "your-dynamodb-table-name"
AWS_REGION = "your-region"

s3 = boto3.client('s3', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        if file:
            filename = str(uuid.uuid4()) + "_" + file.filename
            # Upload to S3
            s3.upload_fileobj(file, S3_BUCKET, filename)
            
            # Save metadata in DynamoDB
            table.put_item(Item={
                'id': str(uuid.uuid4()),
                'filename': filename,
                'upload_time': str(datetime.now()),
                'url': f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"
            })
        return redirect("/")
    
    # Fetch all images
    response = table.scan()
    images = response.get('Items', [])
    return render_template("index.html", images=images)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
