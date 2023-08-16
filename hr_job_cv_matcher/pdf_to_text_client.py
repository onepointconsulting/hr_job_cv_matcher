import requests
from pathlib import Path
import json

from typing import Optional

from hr_job_cv_matcher.config import cfg

from  log_init import logger


def extract_text_from_pdf(pdf: Path) -> Optional[str]:
    if not pdf.exists():
        raise Exception(f"File {pdf} does not exist.")
    with open(pdf, 'rb') as file:
        multipart_form_data = {
            'file': (pdf.name, file)
        }
        response = requests.post(cfg.remote_pdf_server, files=multipart_form_data)
        if response.status_code == 200:
            json_response = json.loads(response.content)
            extracted_text = json_response['extracted_text']
            return extracted_text
        logger.warn("Could not extract PDf content due to %s", response)
        return None