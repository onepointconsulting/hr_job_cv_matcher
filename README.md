# HR Job CV Matcher

This project builds a simple UI to match a Job to a CV using an AI model.

It allows a user to upload a set of job applications and a set of CVs and then it will rank them according to the matching skills specified in
the job description. It will end up creating a sort of ranking matrix matching job description to CVs with the best candidates for a specific 
job description.

This project works best with ChatGPT 4 that can extract at the time of this writing the most accurate matching / missing skills.

## Setup

We suggest to use [https://docs.conda.io/en/latest/](Conda) to manage the virtual environment.

```
conda create -n hr_job_cv_matcher  python=3.11
conda activate hr_job_cv_matcher
pip install poetry
```

## Installation

```
poetry install
```

## Configuration

You will need to have a .env file with the following system variables:

```bash
OPENAI_API_KEY=<open api key>
# OPENAI_MODEL=gpt-3.5-turbo-0613
OPENAI_MODEL=gpt-4-0613
# See https://github.com/gilfernandes/pdf_to_image_server.git which gives you a simple server to convert PDF to images and then extract the text with OCR.
REMOTE_PDF_SERVER=http://176.34.128.143:8086/upload
# Temp document location
TEMP_DOC_LOCATION=/tmp/hr_job_cv_matcher
# Maximum job description files that you can upload
MAX_JD_FILES=5
# Maximum CV files that you can upload
MAX_CV_FILES=20
# The LangChain request timeout
REQUEST_TIMEOUT=120
# Whether the prompts are printed in the logs or not
VERBOSE_LLM=true
# Whether the Langchain cache is to be used or not
LANGCHAIN_CACHE=false
```

## Running

```
chainlit run ./hr_job_cv_matcher/ui/matcher_chainlit.py --port 8087
```