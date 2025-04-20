# VisionScale Projects

This repository contains solutions for two major cloud computing projects, each with two parts, as described in the following documents:

- Project 1 (Part-I)_ IaaS.pdf
- Project 1 (Part-II) (2).pdf
- Project 2 (Part I) PaaS.pdf
- Project 2 (Part II) PaaS.pdf

Each project demonstrates cloud-based architectures, including IaaS and PaaS, with practical implementations using AWS services, Docker, and Python.

---

## Directory Structure

```
VisionScale/
├── Project I part I/
│   ├── Classification_1000.csv
│   ├── handle_request.py
│   └── Project 1 (Part-I)_ IaaS.pdf
├── Project I part II/
│   ├── app_tier.py
│   ├── controller.py
│   ├── web_tier.py
│   └── Project 1 (Part-II) (2).pdf
├── Project II  Part I/
│   ├── Dockerfile
│   ├── handler.py
│   ├── requirements.txt
│   └── Project 2 (Part I) PaaS.pdf
└── Project II  Part II/
    ├── Dockerfile
    ├── handler.py
    ├── requirements.txt
    └── Project 2 (Part II) PaaS.pdf
```

---

## Project Summaries

### Project I (IaaS)
- **Part I**: Implements an image classification service using Flask and a CSV-based lookup. Accepts image uploads and returns classification results. Designed to run on AWS EC2 instances.
- **Part II**: Expands to a multi-tier architecture with web, controller, and app tiers. Implements queue-based scaling of app instances using AWS EC2 and SQS.

### Project II (PaaS)
- **Part I**: Video-to-image Lambda function using AWS Lambda and S3. Extracts a frame from an uploaded video and stores it in S3. Uses Docker for deployment.
- **Part II**: Face recognition Lambda function using AWS Lambda, S3, and PyTorch. Detects and recognizes faces from images, using a pre-trained model. Also Dockerized for deployment.

---

## Setup and Usage

### Prerequisites
- Python 3.8+
- AWS CLI configured with appropriate credentials and permissions
- Docker (for Project II)
- (Optional) Flask for local testing

### Configuration Required Before Running
**Important:** All AWS credentials, bucket names, and queue URLs in the code have been replaced with placeholders, such as:
- `ADD YOUR ACCESS KEY ID`
- `ADD YOUR SECRET KEY`
- `ADD YOUR BUCKET NAME`
- `REQUEST QUEUE URL`
- `RESPONSE QUEUE URL`

Before running any part of the code, you must:
1. Replace all placeholder values in the Python scripts with your actual AWS credentials, S3 bucket names, and SQS queue URLs.
   - **Never commit your real credentials to version control.**
   - For production use, always use environment variables or AWS IAM roles instead of hardcoding sensitive data.
2. Ensure your AWS account has the necessary permissions for S3, SQS, Lambda, and EC2 as required by each project part.

### Project I part I
1. Install dependencies:
   ```bash
   pip install flask
   ```
2. Edit `handle_request.py` to set up any required configuration (see above).
3. Run the Flask server:
   ```bash
   python handle_request.py
   ```
4. Send POST requests with an image file to `/`.

### Project I part II
1. Install dependencies:
   ```bash
   pip install flask boto3
   ```
2. Edit `web_tier.py`, `app_tier.py`, and `controller.py` to set up your AWS credentials, S3 buckets, and SQS queue URLs.
3. Start the web tier:
   ```bash
   python web_tier.py
   ```
4. Controller and app tier are managed/scaled automatically via `controller.py`.

### Project II (Parts I & II)
1. Edit `handler.py` in both parts to set up your AWS credentials and bucket names.
2. Build the Docker image (from the respective folder):
   ```bash
   docker build -t <image-name> .
   ```
3. Run the container (for local testing):
   ```bash
   docker run -p 8080:8080 <image-name>
   ```
4. Deploy to AWS Lambda using the provided Dockerfile and handler.py.

---
