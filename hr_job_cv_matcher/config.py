
from pathlib import Path
import os

from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

from hr_job_cv_matcher.log_init import logger

load_dotenv()


def create_if_not_exists(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

class Config:
    model = os.getenv('OPENAI_MODEL')
    llm = ChatOpenAI(model=model, temperature=0)
    remote_pdf_server = os.getenv('REMOTE_PDF_SERVER')
    temp_doc_location = Path(os.getenv('TEMP_DOC_LOCATION'))
    create_if_not_exists(temp_doc_location)
    max_cv_files = os.getenv('MAX_CV_FILES') or 10


cfg = Config()

if __name__ == "__main__":
    logger.info("Model: %s", cfg.model)
    logger.info("Remote_pdf_server: %s", cfg.remote_pdf_server)
    logger.info("Max CV Files: %s", cfg.max_cv_files)