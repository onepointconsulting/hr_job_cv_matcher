# HR Job CV Matcher

This project builds a simple UI to match a Job to a CV using an AI model.

It allows a user to upload a set of job applications and a set of CVs and then it will rank them according to the matching skills specified in
the job description. It will end up creating a sort of ranking matrix matching job description to CVs with the best candidates for a specific 
job description.

This project works best with ChatGPT 4 that can extract at the time of this writing the most accurate matching / missing skills.

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