# DevOps Video to Audio Converter

A polished end-to-end project that turns uploaded videos into downloadable MP3 files with a cloud-native DevOps pipeline.

This repository demonstrates:

- a Flask upload service for video intake
- Apache Kafka for job queuing
- FFmpeg-based audio conversion
- AWS S3 for storage and presigned downloads
- k3s Kubernetes deployment via Ansible
- Terraform cloud infrastructure provisioning

---

## 🚀 What this project does

A user uploads a video through the web UI, the app stores it in S3, and publishes a Kafka job. A converter worker consumes the job, runs FFmpeg, uploads the MP3 back into S3, and returns a secure presigned download link.


## 🧠 Architecture Overview
<p align="center">
  <img width="720" height="800" alt="Screenshot 2026-04-27 at 4 25 48 AM" src="https://github.com/user-attachments/assets/4fbb9abc-bc2f-48f7-9f13-8c5ad2e9d9d4" />

</p>


### Flow Summary

1. **Upload Service** receives a `.mp4` file
2. **S3** stores the original video
3. **Kafka** queues the conversion job on `video-jobs`
4. **Converter Service** consumes the job and runs `ffmpeg`
5. Converted MP3 is uploaded to **S3**
6. User gets a **presigned URL** for download

---



## 📁 Repository Structure

- `app/upload-service` — Flask upload UI and Kafka producer
- `app/converter-service` — Kafka consumer and FFmpeg converter
- `ansible` — automation to install Docker, k3s, and deploy the app
- `k8s` — Kubernetes manifests for service and deployment resources
- `terraform` — cloud infrastructure provisioning
- `deploy.sh` — helper script for build/deploy tasks

---

## 🖼️ Demo Screens

<p align="center">
  <img width="1822" height="1097" alt="Screenshot 2026-04-27 at 3 35 49 AM" src="https://github.com/user-attachments/assets/6d3e706e-d414-4c34-83d9-893d716f4558" />
</p>

<p align="center">
  <img width="1600" height="997" alt="WhatsApp Image 2026-05-22 at 23 17 31" src="https://github.com/user-attachments/assets/7bf803e0-ac97-4176-9735-0cb057af023a" />

</p>

<p align="center">
 <img width="3364" height="2194" alt="WhatsApp Image 2026-05-22 at 23 32 57" src="https://github.com/user-attachments/assets/6c641a82-48e1-4ddc-9fe6-e2a9534cb58e" />

</p>

---

## ⚙️ Quick Start

### Prerequisites

- Python 3
- Docker
- Terraform
- Ansible
- AWS credentials with S3 access
- `ffmpeg` available in converter runtime

### Environment variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
export S3_BUCKET="video-audio-converter-yourname-2024"
export KAFKA_BROKER="kafka:9092"
```

### Local Run

1. Start the Flask upload service

```bash
cd app/upload-service
python3 -m pip install -r requirements.txt
python3 app.py
```

2. Start the converter worker

```bash
cd app/converter-service
python3 -m pip install -r requirements.txt
python3 worker.py
```

3. Ensure Kafka is available

- Set `KAFKA_BROKER` to your Kafka endpoint, e.g. `localhost:9092`.

4. Open the web UI and upload a video

```bash
http://localhost:5000
```

> The Flask app currently provides a simple UI for upload and status lookup.

---

## 🐳 Docker Run Example

Run both services in containers with Docker:

```bash
cd app/upload-service
docker build -t video-upload .

docker run -d --name upload-service \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e AWS_REGION="$AWS_REGION" \
  -e S3_BUCKET="$S3_BUCKET" \
  -e KAFKA_BROKER="$KAFKA_BROKER" \
  -p 5000:5000 video-upload

cd app/converter-service
docker build -t converter-worker .

docker run -d --name converter-service \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e AWS_REGION="$AWS_REGION" \
  -e S3_BUCKET="$S3_BUCKET" \
  -e KAFKA_BROKER="$KAFKA_BROKER" \
  converter-worker
```

---

## ☁️ Infrastructure & Deployment

### Terraform

Use the `terraform/` directory to provision infrastructure resources such as EC2, S3 buckets, and networking.

### Ansible

The `ansible/playbook.yml` installs Docker, k3s, and applies Kubernetes manifests. It also creates Kubernetes secrets for AWS credentials and bucket configuration.

---

## 💡 Best Practices

- Keep AWS secrets out of Git
- Use `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in environment variables
- Do not store production credentials in `ansible/playbook.yml`
- Use a dedicated S3 bucket for input and output storage

---

