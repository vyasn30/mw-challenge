# FastAPI Logging Service

This FastAPI application provides a logging service that ingests, processes, and stores log data efficiently. It utilizes Redis for caching log messages and AWS S3 for persistent storage. The service supports ingesting logs in batches and querying stored logs based on specific criteria.

## Features

- Log ingestion via a RESTful API.
- Background processing of log messages to sort and store them in AWS S3.
- Querying stored logs within a specified time range and text search.
- Download functionality for retrieving logs stored in S3.

## Installation

### Prerequisites

- Python 3.8+
- Redis server
- AWS account with S3 access
- `.env` file with AWS credentials and Redis configuration

### Setup

1. Clone the repository:

    ```
    git clone https://github.com/your-repository/fastapi-logging-service.git
    ```

    ```
    cd fastapi-logging-service
    ```

2. Install required packages:

    ```
    pip install -r requirements.txt
    ```

3. Configure your `.env` file with the necessary environment variables:
    ```
    S3_Bucket_Name=your_bucket_name
    Secret=your_aws_secret_access_key
    Region=your_aws_region
    Folder_Name=your_log_folder_name
    ```

4. Ensure your Redis server is running and accessible.

## Running the Application

To run the FastAPI server, execute the following command:
```
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Limitations

- The current implementation is a basic version and does not include authentication or authorization for API access.
- Log querying is performed via simple string matching, which may not be efficient for large datasets.
- The system is dependent on AWS S3 and Redis, limiting its flexibility in terms of storage options.

## Future Improvements

- **Security Enhancements:** Implement JWT-based authentication to secure API endpoints.
- **Advanced Search Capability:** Integrate Elasticsearch or similar technologies for efficient log searching capabilities.
- **Scalability:** Add support for horizontal scaling by integrating with a message broker such as RabbitMQ or Kafka for distributed processing.
- **Storage Flexibility:** Abstract storage layer to support multiple backends beyond AWS S3, like Azure Blob Storage or Google Cloud Storage.
- **Monitoring and Alerting:** Integrate monitoring tools like Prometheus and alerting mechanisms to track the health of the service.

## Contributing

We welcome contributions! Please open an issue or submit a pull request for any features, bug fixes, or improvements.