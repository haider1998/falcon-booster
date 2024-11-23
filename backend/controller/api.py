# backend/api.py
import logging
import os
import uuid

from fastapi import FastAPI, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config.logging_config import configure_logging
from backend.main import WorkflowRunner
from backend.services.file_service import FileService
from backend.services.git_connect import GitConnect
from backend.services.json_service import JsonService
from backend.services.mermaid_service import MermaidService
from backend.services.sql_file_processor_service import SQLFileProcessor

app = FastAPI()

# Mount the static files directory
app.mount("/images", StaticFiles(directory="frontend/images"), name="images")
app.mount("/components", StaticFiles(directory="frontend/components"), name="components")

# Load the Jinja2 templates
templates = Jinja2Templates(directory="frontend")

# Configure logging
correlation_filter = configure_logging()

# Initialize services
git_service = GitConnect()
sql_processor = SQLFileProcessor
json_service = JsonService()
mermaid_service = MermaidService()

# Initialize WorkflowRunner
runner = WorkflowRunner(git_service, sql_processor, json_service, mermaid_service)


@app.middleware("http")
async def add_correlation_ids(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    session_id = request.headers.get('X-Session-ID', str(uuid.uuid4()))
    correlation_filter.set_correlation_ids(request_id, session_id)
    response = await call_next(request)
    return response


@app.get("/", response_class=HTMLResponse)
async def get_form():
    try:
        with open("frontend/index.html") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Form not found")


@app.post("/", response_class=HTMLResponse)
async def post_form(
        request: Request,
        github_url: str = Form(...),
        app_name: str = Form(...),
        feed_name: str = Form(...),
        initials_6char: str = Form(...),
        ccpa: bool = Form(False),
        dropzone_gcs_bucket: bool = Form(False),
        dropzone_sftp: bool = Form(False),
        action: str = Form(...)
):
    try:
        logging.debug(f"GitHub URL: {github_url}")
        logging.debug(f"CCPA: {ccpa}")
        logging.debug(f"Dropzone SFTP: {dropzone_sftp}")
        logging.debug(f"GCS Bucket: {dropzone_gcs_bucket}")
        logging.debug(f"Action: {action}")

        os.makedirs('tmp/de', exist_ok=True)
        #Clear Resource/Temp Folder
        runner.clear_resources()

        if action == "design":
            mermaid_code = runner.runflow(github_url, app_name, feed_name, initials_6char, ccpa, 'mmd', dropzone_gcs_bucket,
                                          dropzone_sftp)
            return templates.TemplateResponse(
                "diagram.html",
                {
                    "request": request,
                    "mermaid_code": mermaid_code,
                    "design_name": f"Design_{app_name}_{feed_name}",
                },
                status_code=status.HTTP_200_OK
            )
        elif action == "details":
            data = runner.runflow(github_url, app_name, feed_name, initials_6char, ccpa,
                                  'json', dropzone_gcs_bucket, dropzone_sftp)  # This should be a dictionary with a 'steps' key
            steps = data.get('steps', [])  # Get the list of steps

            return templates.TemplateResponse(
                "result.html",
                {
                    "request": request,
                    "steps": steps,
                    "app_name": app_name,
                    "feed_name": feed_name,
                    "initials_6char": initials_6char,
                    "ccpa": ccpa
                },
                status_code=status.HTTP_200_OK
            )
    except Exception as e:
        return templates.TemplateResponse(
            "failure.html",
            {
                "request": request,
                "error_message": f"{e}",
                "request_correlation_id": correlation_filter.get_request_id(),
                "session_correlation_id": correlation_filter.get_session_id()
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get("/create-feed-repository", response_class=HTMLResponse)
async def get_create_feed_repository_form():
    try:
        with open("frontend/create_feed_repository.html") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Form not found")


@app.post("/create-feed-repository", response_class=HTMLResponse)
async def create_feed_repository(
        request: Request,
        app_name: str = Form(...),
        feed_name: str = Form(...),
        initials_6char: str = Form(...),
        ccpa: bool = Form(),
        data_engineer_name: str = Form(...),
        data_engineer_cds_id: str = Form(...),
        software_engineer_cds_id: str = Form(...),
        storage_type: str = Form(...)

):
    try:
        # Log the received data
        logging.debug(f"App Name: {app_name}")
        logging.debug(f"Feed Name: {feed_name}")
        logging.debug(f"Initials: {initials_6char}")
        logging.debug(f"Data Engineer Name: {data_engineer_name}")
        logging.debug(f"Data Engineer CDS Id: {data_engineer_cds_id}")
        logging.debug(f"Software Engineer CDS Id: {software_engineer_cds_id}")
        logging.debug(f"Storage Type: {storage_type}")
        logging.debug(f"CCPA: {ccpa}")

        dfa_feed_repo_name = f"50884_{app_name.lower().replace('gcp', 'dfa').replace('-', '_')}_{feed_name.lower().replace('-', '_')}"
        file_service = FileService(f'tmp/resource/{dfa_feed_repo_name}/scripts/sql', app_name, feed_name,
                                   initials_6char, dfa_feed_repo_name, data_engineer_name, data_engineer_cds_id,
                                   software_engineer_cds_id, storage_type, ccpa)

        file_service.create_feed_repository()

        # Process the data as needed
        # For example, you can call a service to create the feed repository
        # result = some_service.create_feed_repository(...)

        # Return a success response
        return templates.TemplateResponse(
            "success_git_repo_creation.html",
            {
                "request": request,
                "message": "Feed repository created successfully!"
            },
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return templates.TemplateResponse(
            "failure.html",
            {
                "request": request,
                "error_message": f"{e}",
                "request_correlation_id": correlation_filter.get_request_id(),
                "session_correlation_id": correlation_filter.get_session_id()
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
