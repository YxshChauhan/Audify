# app/converter-service/worker.py
from kafka import KafkaConsumer
import boto3, subprocess, json, os, time

# Wait for Kafka to be ready
time.sleep(20)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)

consumer = KafkaConsumer(
    'video-jobs',
    bootstrap_servers=[os.environ.get('KAFKA_BROKER', 'kafka:9092')],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='converter-group'
)

print("Converter worker started. Waiting for jobs...")

for message in consumer:
    job = message.value
    print(f"Processing job: {job['job_id']}")

    try:
        input_path = f"/tmp/{job['job_id']}_input"
        output_path = f"/tmp/{job['job_id']}_output.mp3"

        # Download video from S3
        s3.download_file(job['bucket'], job['s3_key'], input_path)

        # Convert to mp3 using FFmpeg
        result = subprocess.run([
            'ffmpeg', '-i', input_path,
            '-vn',                    # no video
            '-acodec', 'libmp3lame', # mp3 codec
            '-ab', '192k',           # bitrate
            '-y',                    # overwrite output
            output_path
        ], capture_output=True, text=True)

        if result.returncode == 0:
            audio_key = f"audio/{job['job_id']}/output.mp3"
            s3.upload_file(output_path, job['bucket'], audio_key)
            print(f"Done! Audio saved to s3://{job['bucket']}/{audio_key}")
        else:
            print(f"FFmpeg error: {result.stderr}")

        # Cleanup temp files
        os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

    except Exception as e:
        print(f"Error processing job {job['job_id']}: {e}")