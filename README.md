# Falcon Booster

![Falcon Booster Logo](https://github.com/haider1998/falcon-booster/frontend/images/falcon-logo-removebg-preview.png)

[![License](https://img.shields.io/github/license/haider1998/falcon-booster)](LICENSE)
[![Build Status](https://github.com/haider1998/falcon-booster/actions/workflows/ci.yml/badge.svg)](https://github.com/haider1998/falcon-booster/actions)
[![Coverage Status](https://codecov.io/gh/haider1998/falcon-booster/branch/main/graph/badge.svg)](https://codecov.io/gh/haider1998/falcon-booster)
[![Docker Pulls](https://img.shields.io/docker/pulls/haider1998/falcon-booster)](https://hub.docker.com/r/haider1998/falcon-booster)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
  - [Local Deployment](#local-deployment)
  - [GCP Cloud Run Deployment](#gcp-cloud-run-deployment)
- [Testing](#testing)
- [Continuous Integration](#continuous-integration)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Introduction

**Falcon Booster** is a web-based service that automates the generation of design diagrams and workbooks for GCP Cloud Composer or Apache Airflow feeds. Built on the high-performance [FastAPI](https://fastapi.tiangolo.com/) framework, Falcon Booster significantly reduces the time and effort required for manual documentation, enhancing developer productivity and ensuring consistent, accurate documentation across projects. By analyzing a provided GitHub repository, Falcon Booster can generate comprehensive documentation in under 30 seconds, compared to the 2-3 hours typically required when done manually.

## Features

- **Automatic Documentation Generation**: Transforms a GitHub repository and basic feed information into comprehensive design diagrams and workbooks in under 30 seconds.
- **Efficient Codebase Analysis**: Analyzes codebases and dependencies to produce accurate and consistent documentation.
- **Web-Based Interface**: Accessible through an intuitive web interface for ease of use.
- **Feed Repository Creation**: Provides tools to automatically create feed repositories with standard structure and configurations.
- **Time Saving**: Reduces documentation time from 3 hours to 30 seconds, saving approximately 60-66 hours per sprint.
- **Cloud-Native Deployment**: Optimized for deployment on GCP Cloud Run for scalable and serverless execution.
- **RESTful API Endpoints**: Provides easy-to-use API endpoints for integration with other tools and services.
- **Robust Logging and Error Handling**: Includes request correlation IDs for effective logging and troubleshooting.

## Architecture

![Architecture Diagram](https://github.com/haider1998/falcon-booster/raw/main/docs/images/architecture.png)

The Falcon Booster application follows a modern web application architecture optimized for cloud deployment. Key components include:

- **Frontend**: HTML templates served using Jinja2 for rendering dynamic web pages.
- **Backend**: Built with FastAPI, providing an asynchronous web server with high performance.
- **Services**: Modular services for Git operations, SQL processing, JSON handling, and diagram generation.
- **Workflow Runner**: Coordinates the services to execute the main functionality.
- **Logging Configuration**: Implements structured logging with correlation IDs for tracing requests and sessions.
- **Deployment**: Containerized with Docker and deployed on GCP Cloud Run for serverless operation and auto-scaling.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Git**
- **Docker** (for containerization and deployment)
- **GCP Account** (for deploying on Cloud Run)
- **Google Cloud SDK** (for interacting with GCP services)
- **Make** (optional, for using the provided Makefile)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/haider1998/falcon-booster.git
   ```

2. **Navigate to the project directory**

   ```bash
   cd falcon-booster
   ```

3. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the root directory and add the following configurations:

```dotenv
# .env file

# Application Settings
APP_ENV=development
APP_DEBUG=True

# GCP Settings
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1

# GitHub Settings
GITHUB_TOKEN=your-github-token  # Required if accessing private repositories or to increase API rate limits

# Other Settings
LOGGING_LEVEL=INFO
```

## Usage

Run the application locally:

```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

The application will start on `http://localhost:8000`.

### Web Interface

#### Home Page

Access the home page at `http://localhost:8000/`. Here you can:

- **Generate Design Diagrams**: Provide your GitHub repository URL and feed details to generate mermaid diagrams.
- **View Feed Details**: Get detailed steps and configurations extracted from your codebase.

#### Create Feed Repository

Access the feed repository creation page at `http://localhost:8000/create-feed-repository`. Here you can:

- **Create a New Feed Repository**: Input necessary information to automatically create a standardized feed repository.

### API Endpoints

- `GET /`: Returns the HTML form for inputting GitHub URL and feed information.
- `POST /`: Processes the form data and performs actions based on the submitted data.
  - **Parameters**:
    - `github_url`: The URL of the GitHub repository.
    - `app_name`: The application name.
    - `feed_name`: The feed name.
    - `initials_6char`: Your initials (up to 6 characters).
    - `ccpa`: Boolean indicating if CCPA applies.
    - `dropzone_gcs_bucket`: Boolean indicating if GCS bucket is used.
    - `dropzone_sftp`: Boolean indicating if SFTP is used.
    - `action`: The action to perform (`design` or `details`).
- `GET /create-feed-repository`: Returns the HTML form for creating a new feed repository.
- `POST /create-feed-repository`: Processes the form data to create a new feed repository.

## Deployment

### Local Deployment

#### Using Docker

1. **Build the Docker image**

   ```bash
   docker build -t haider1998/falcon-booster:latest .
   ```

2. **Run the Docker container**

   ```bash
   docker run -d -p 8000:8000 --env-file .env haider1998/falcon-booster:latest
   ```

### GCP Cloud Run Deployment

1. **Authenticate with Google Cloud**

   ```bash
   gcloud auth login
   gcloud config set project your-gcp-project-id
   ```

2. **Build and Submit the Image to Google Container Registry**

   ```bash
   gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/falcon-booster
   ```

3. **Deploy to Cloud Run**

   ```bash
   gcloud run deploy falcon-booster \
     --image gcr.io/$GCP_PROJECT_ID/falcon-booster \
     --platform managed \
     --region $GCP_REGION \
     --allow-unauthenticated \
     --set-env-vars $(cat .env | tr '\n' ',' | sed 's/,$//')
   ```

**Notes**:

- Ensure that the service account used by Cloud Run has the necessary permissions to access any required resources.
- Securely manage your environment variables and secrets, especially the `GITHUB_TOKEN`. Consider using GCP Secret Manager for sensitive data.

## Testing

Run unit tests using `pytest`:

```bash
pytest
```

To run integration tests:

```bash
pytest tests/integration
```

To run end-to-end tests:

```bash
pytest tests/e2e
```

## Continuous Integration

This project uses GitHub Actions for Continuous Integration and Continuous Deployment.

- **CI Workflow**: Automatically runs on push to the `main` branch, executing linting, testing, and building the Docker image.
- **CD Workflow**: Upon successful CI, the Docker image is pushed to Google Container Registry, and the service is deployed to GCP Cloud Run.

Badges:

[![Build Status](https://github.com/haider1998/falcon-booster/actions/workflows/ci.yml/badge.svg)](https://github.com/haider1998/falcon-booster/actions)
[![Coverage Status](https://codecov.io/gh/haider1998/falcon-booster/branch/main/graph/badge.svg)](https://codecov.io/gh/haider1998/falcon-booster)

## Contributing

We welcome contributions from the community! Please follow these steps:

1. **Fork the repository**.

2. **Create a feature branch**:

   ```bash
   git checkout -b feature/<feature_name>
   ```

3. **Commit your changes**:

   ```bash
   git commit -m "Add <feature_name>"
   ```

4. **Push to your branch**:

   ```bash
   git push origin feature/<feature_name>
   ```

5. **Open a Pull Request**.

Please ensure all tests pass and adhere to the project's coding standards before submitting a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [GitPython](https://gitpython.readthedocs.io/)
- [Google Cloud Platform](https://cloud.google.com/)
- [GitHub Actions](https://github.com/features/actions)
- **Contributors**: [haider1998](https://github.com/haider1998)

## Contact

**Author**: Syed Mohd Haider Rizvi

- **Email**: [smhrizvi281@gmail.com](mailto:smhrizvi281@gmail.com)
- **LinkedIn**: [Syed Mohd Haider Rizvi](https://www.linkedin.com/in/s-m-h-rizvi-0a40441ab/)
- **GitHub**: [haider1998](https://github.com/haider1998)

---

Thank you for your interest in Falcon Booster! If you have any questions or need assistance, please feel free to reach out.

---

## Additional Notes

- **Template Files**:

  - Ensure that the templates (`index.html`, `diagram.html`, `result.html`, `failure.html`, `create_feed_repository.html`, `success_git_repo_creation.html`) are correctly placed in the `frontend` directory.

- **Static Files**:

  - Static images and components are served from the `frontend/images` and `frontend/components` directories respectively.

- **Middleware**:

  - The application uses middleware to add correlation IDs for requests and sessions for better tracing and logging.

- **Logging Configuration**:

  - Logging is configured via `backend.config.logging_config`. Ensure that your logs are properly output and managed, especially when running in production.

- **Session Management**:

  - Session IDs are generated per request. For persistent sessions, consider integrating a session management system.

- **Error Handling**:

  - The application includes exception handling to return appropriate templates in case of errors, with HTTP status codes.

- **Security Considerations**:

  - Validate and sanitize all user inputs to prevent security vulnerabilities such as injection attacks.
  - Use HTTPS in production environments to secure data in transit.
  - Securely store and manage sensitive information like API tokens and credentials.

- **Important Directories**:

  - `backend/`: Contains the FastAPI application code, services, and configurations.
  - `frontend/`: Contains HTML templates, static files, images, and components.
  - `tmp/`: Used for temporary storage during processing. Ensure this directory is managed appropriately in production environments.

## Code Overview

Here's a brief overview of the main application code to help you understand how everything fits together.

### `backend/api.py`

This is the main entry point of the FastAPI application.

- **Imports** necessary modules and initializes the FastAPI app.
- **Mounts** static files and templates using Jinja2.
- **Configures Logging** with correlation IDs for tracing.
- **Initializes Services**:
  - `GitConnect`
  - `SQLFileProcessor`
  - `JsonService`
  - `MermaidService`
- **Defines Middleware** to add correlation IDs to each request.
- **Defines Routes**:
  - `GET /`: Renders the main form for input.
  - `POST /`: Processes form data and performs actions (`design` or `details`).
  - `GET /create-feed-repository`: Renders the form to create a new feed repository.
  - `POST /create-feed-repository`: Processes data to create a new feed repository.
- **Exception Handling**: Returns `failure.html` in case of exceptions, along with error messages and correlation IDs.

### Services

- **`GitConnect`**: Manages interactions with Git repositories.
- **`SQLFileProcessor`**: Processes SQL files within the repository.
- **`JsonService`**: Handles JSON data manipulation.
- **`MermaidService`**: Generates diagram code in Mermaid syntax.
- **`FileService`**: Handles file creation and manipulation for feed repositories.

### Workflow Runner

- **`WorkflowRunner`**: Coordinates the different services to execute the main logic of generating documentation or details based on the provided repository and parameters.

---

By following best engineering practices, Falcon Booster is designed to be efficient, scalable, and easy to maintain. The service leverages the power of GCP Cloud Run for serverless deployment, ensuring optimal resource utilization and cost-effectiveness.

If you have any suggestions or encounter any issues, please open an issue on the [GitHub repository](https://github.com/haider1998/falcon-booster/issues).

---
