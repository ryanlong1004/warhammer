# warhammer

## File Processing and Task Submission Script

This Python script processes files in a specified directory, sends each file as a task to a server for processing, and checks the status of each task until completion.

### Requirements

- Python 3.6 or later
- The following Python packages:
  - `requests`
  - `loguru`

To install the necessary packages, you can use:

```bash
pip install -r requirements.txt
```

## Script Usage

Run the script from the command line with the following options:

```bash
python script.py --directory /path/to/files --max-tasks 5
```

## Command-Line Arguments

```
--directory (-d): Directory containing files to process.

Default: ./test
Example: /path/to/your/directory
--max-tasks (-m): Maximum number of tasks to process.

Default: 1
Example: 5
```

## Example Command

To process files in a directory named videos and limit to 3 tasks, run:

```bash
python script.py --directory ./videos --max-tasks 3
```
# warhammer
