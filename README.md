# DNSWatch Prototype

## Overview
DNSWatch Prototype is a comprehensive solution for setting up a custom DNS server with full telemetry of user data. This repository includes all the necessary steps, configurations, and code required for deployment.

## Project Requirements
The project consists of several key components:

1. **AWS Global Accelerator** – Provides the best latency and easy accessibility by deploying the server across multiple regions using edge locations.
2. **DnsDist Server** – Balances the load of incoming DNS queries and directs them to the appropriate backend resolver.
3. **PowerDNS Server** – Resolves DNS queries and blocks unwanted queries, returning custom responses.
4. **Fluent-bit** – Configures logging and forwards logs to AWS Kinesis Stream.
5. **AWS Kinesis Stream** – Captures logs and routes them to an S3 bucket via Firehose.
6. **AWS Step Functions** – Automates the process of transferring data from S3 to an RDS (PostgreSQL) database for storage and analysis.

---

## 1. Global Accelerator
**AWS Global Accelerator** is a networking service that provides a static IP for routing DNS requests to the appropriate server.

### Configuration Steps:
- Configure **Global Accelerator** with **UDP port 53** (DNS port).
- Attach the Global Accelerator endpoint to the EC2 instance where DnsDist is deployed.

---

## 2. DnsDist Server
DnsDist is a high-performance load balancer for DNS queries, providing additional security and flexibility via Lua scripting.

### Installation & Configuration:
- Install **DnsDist version 1.9.X**.
- Modify the configuration file located at `/etc/dnsdist/dnsdist.conf`.
- Configure DnsDist to:
  - Forward queries to the PowerDNS server.
  - Log DNS query requests for telemetry purposes.

Refer to the repository's **dnsdist.conf** file for detailed configuration.

---

## 3. PowerDNS Server
PowerDNS is an open-source DNS resolver with extensive customization options. The **PowerDNS Recursor** is used in this setup.

### Installation & Configuration:
- Install **PowerDNS Recursor version 5.0** on an EC2 machine.
- Modify `/etc/powerdns/recursor.conf` with custom settings.
- Implement custom Lua scripts:
  - `preresolve.lua` – Executes before resolving a request.
  - `postresolve.lua` – Executes after resolving a request.
- Deploy PowerDNS using Docker:
  - Create a Docker image and push it to AWS ECR.
  - Deploy the image as an **ECS Fargate Task** for scalability.

Configuration files and scripts can be found in the **powerdns/** directory of this repository.

---

## 4. Fluent-bit
Fluent-bit is used for log processing, formatting, and forwarding DNS logs to AWS Kinesis Stream.

### Installation & Configuration:
- Install Fluent-bit.
- Update the configuration file at `/etc/fluent-bit/fluent-bit.conf`.
- Create a custom parser (`powerdns`) in `/etc/fluent-bit/parser.conf`.
- Configure Fluent-bit to:
  - Accept logs via a **TCP input** from PowerDNS.
  - Forward logs to **AWS Kinesis Stream**.
- Deploy Fluent-bit using Docker:
  - Create a Docker image and run it as an **ECS Fargate Task**.

Refer to **fluent-bit/fluent-bit.conf** for full configuration details.

---

## 5. AWS Kinesis Stream
AWS Kinesis Stream is used to collect and process log data.

### Configuration:
- Create a **Kinesis Data Stream** in AWS.
- Attach **Kinesis Firehose** to send logs from the stream to an **S3 bucket**.

---

## 6. AWS Step Functions
Step Functions automate the data pipeline from S3 to RDS.

### Workflow:
1. **Crawler** scans the S3 bucket to detect schema changes.
2. **AWS Athena** queries the data.
3. **Query results** are stored in an S3 bucket.
4. **Step Function** extracts the query result key and invokes a Lambda function.
5. **Lambda Function** reads the S3 file and loads data into **RDS (PostgreSQL)**.
6. **Lambda Layer** is used for dependency management.

### Key Details:
- **Step Function Execution Interval**: Every **5 minutes**.
- **Event Format** for Lambda:
  ```json
  {
    "s3_key": {
      "S3Key": "s3://athena-result/005f791c-d609-4831-baeb-d70d29ead1ea.csv"
    }
  }
  ```
- Environment variables should be configured as per the project requirements.

Refer to the **lambda_function.py** and **requirements.txt** in the repository for the Lambda code.

---

## Summary
This project enables a **custom DNS server** with telemetry capabilities, ensuring:
- Efficient **DNS resolution and blocking** of unwanted queries.
- **Scalable infrastructure** using AWS services.
- **Comprehensive logging and monitoring** via Fluent-bit and Kinesis.
- **Automated data ingestion** into an RDS database using AWS Step Functions.

For full configuration details, refer to the corresponding directories and files in this repository.

