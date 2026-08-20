from flask import Flask, request, jsonify, redirect
from kafka import KafkaProducer
import boto3, uuid, json, os

app = Flask(__name__)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)

BUCKET = os.environ['S3_BUCKET']

# Lazy producer — only connects when first upload happens
_producer = None

def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=[os.environ.get('KAFKA_BROKER', 'kafka:9092')],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    return _producer

@app.route('/', methods=['GET'])
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video to Audio Converter</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                max-width: 500px;
                width: 100%;
            }
            h2 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }
            .section {
                margin-bottom: 30px;
            }
            .section h3 {
                color: #555;
                margin-bottom: 15px;
            }
            input[type="file"] {
                display: block;
                margin: 10px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                width: 100%;
                box-sizing: border-box;
            }
            input[type="text"] {
                display: block;
                margin: 10px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                width: 100%;
                box-sizing: border-box;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
            }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Video to Audio Converter</h2>
            <div class="section">
                <h3>Upload Video for Conversion</h3>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="video" accept="video/*" required>
                    <button type="submit">Convert to MP3</button>
                </form>
            </div>
            <div class="section">
                <h3>Download Converted Audio</h3>
                <form action="/check_status" method="get">
                    <input type="text" name="job_id" placeholder="Enter Job ID" required>
                    <button type="submit">Check Status & Download</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400

    file = request.files['video']
    job_id = str(uuid.uuid4())
    s3_key = f"videos/{job_id}/{file.filename}"

    s3.upload_fileobj(file, BUCKET, s3_key)

    get_producer().send('video-jobs', {
        'job_id': job_id,
        's3_key': s3_key,
        'bucket': BUCKET,
        'original_name': file.filename
    })
    get_producer().flush()

    return jsonify({
        'job_id': job_id,
        'message': 'Video uploaded! Audio will be ready shortly.',
        'check_url': f'/status/{job_id}'
    })

@app.route('/check_status', methods=['GET'])
def check_status_form():
    job_id = request.args.get('job_id')
    if not job_id:
        return '<h2>Error</h2><p>Job ID is required.</p><a href="/">Back</a>', 400
    return redirect(f'/status/{job_id}')

@app.route('/status/<job_id>', methods=['GET'])
def check_status(job_id):
    try:
        audio_key = f"audio/{job_id}/output.mp3"
        url = s3.generate_presigned_url('get_object',
            Params={'Bucket': BUCKET, 'Key': audio_key},
            ExpiresIn=3600)
        return f'''
        <!DOCTYPE html><html><head><meta charset="UTF-8">
        <title>Done</title>
        <style>
            body{{font-family:Arial,sans-serif;background:#f4f4f4;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}}
            .container{{background:white;padding:40px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);max-width:500px;width:100%;text-align:center}}
            a{{display:inline-block;background:#007bff;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;margin:10px}}
            a:hover{{background:#0056b3}}
            .success{{background:#d4edda;color:#155724;padding:15px;border-radius:5px;margin:20px 0}}
        </style></head>
        <body><div class="container">
            <h2>Conversion Complete!</h2>
            <div class="success">Your audio file is ready for download.</div>
            <a href="{url}">Download MP3</a><br>
            <a href="/">Back to Home</a>
        </div></body></html>
        '''
    except:
        return '''
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Processing</title>
        <style>
            body{{font-family:Arial,sans-serif;background:#f4f4f4;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}}
            .container{{background:white;padding:40px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);max-width:500px;width:100%;text-align:center}}
            a{{display:inline-block;background:#6c757d;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;margin-top:20px}}
            .processing{{background:#fff3cd;color:#856404;padding:15px;border-radius:5px;margin:20px 0}}
        </style></head>
        <body><div class="container">
            <h2>Still Processing...</h2>
            <div class="processing">Your video is still being converted. Please check back in a moment.</div>
            <a href="/">Back to Home</a>
        </div></body></html>
        '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)