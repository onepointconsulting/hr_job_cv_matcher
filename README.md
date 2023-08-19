# HR Job CV Matcher

This project builds a simple UI to match a Job to a CV using an AI model.

## Setup

```
conda create -n hr_job_cv_matcher  python=3.11
conda activate hr_job_cv_matcher
pip install poetry
```

## Installation

```
poetry install
```

## Running

```
chainlit run ./hr_job_cv_matcher/ui/matcher_chainlit.py --port 8087
```