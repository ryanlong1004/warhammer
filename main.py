"""main"""

import json
import time
from pathlib import Path
from queue import Queue
from typing import Generator, Optional

import requests
from loguru import logger
import argparse

# Initialize a queue
task_queue = Queue()

logger.add("warhammer.log", retention="3 days")  # Add a file sink


def get_files(directory: Path) -> Generator[Path, None, None]:
    """Yield all files in the directory and its subdirectories."""
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            yield file_path


def submit_task(file_path: Path) -> Optional[str]:
    """Send a file to the detection endpoint and return the task ID if successful."""
    url = "http://192.168.5.247:3001/detect"
    logger.info(f"Submitting file: {file_path}")

    try:
        with file_path.open("rb") as file:
            files = {"file": file}
            data = {"model_size": "small", "translate": "false", "vad": "false"}
            response = requests.post(
                url,
                files=files,
                data=data,
                headers={"accept": "application/json"},
                timeout=30,
            )

        if response.ok:
            result = response.json()
            logger.debug(f"Response received: {result}")
            if result.get("status") == "pending":
                return result.get("task_id")
            logger.error("Submission failed, no pending status.")
        else:
            logger.error(f"Error in request: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.exception(f"Request failed for file {file_path}: {e}")
    return None


def check_task_status(task_id: str) -> Optional[dict]:
    """Check the status of a task by task ID."""
    url = f"http://192.168.5.247:3001/status/{task_id}"
    logger.info(f"Checking status for task ID: {task_id}")

    try:
        response = requests.get(url, headers={"accept": "application/json"}, timeout=30)
        if response.ok:
            return response.json()
        logger.error(f"Error checking status: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.exception(f"Failed to get status for task ID {task_id}: {e}")
    return None


def process_files(directory: Path, max_tasks: int = 1):
    """Process files in a directory, submitting each to the task queue and checking status."""
    for count, file_path in enumerate(get_files(directory), start=1):
        task_id = submit_task(file_path)
        if not task_id:
            logger.warning(f"Task submission failed for file: {file_path}")
            continue

        while True:
            time.sleep(10)
            try:
                result = check_task_status(task_id)
            except Exception as e:
                print(e)
                exit()
            if not result:
                logger.warning("*** Task not found or request failed ***")
                continue

            status = result.get("status")
            if status in ["pending", "processing"]:
                logger.info(f"Task {task_id} is still {status}.")
            else:
                logger.info(f"Task {task_id} completed with status: {status}")
                logger.debug(f"Result: {json.dumps(result, indent=2)}")
                break

        if count >= max_tasks:
            break


def main():
    # Set up CLI argument parsing
    parser = argparse.ArgumentParser(
        description="Process files and send tasks to a server."
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        default=Path("./test"),
        help="Directory containing files to process (default: ./test)",
    )
    parser.add_argument(
        "-m",
        "--max-tasks",
        type=int,
        default=1,
        help="Maximum number of tasks to process (default: 1)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Start processing files with parsed arguments
    logger.info("Starting file processing...")
    process_files(args.directory, args.max_tasks)


if __name__ == "__main__":
    main()
