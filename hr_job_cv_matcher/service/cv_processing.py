from typing import List, Dict, Callable
from hr_job_cv_matcher.service.job_description_cv_matcher import create_input_list


def process_multiple_cvs(job_description: str, cvs: List[str], llm_chain_func: Callable) -> List[Dict]:
    assert job_description is not None, "Job description is not available"
    assert len(cvs) > 0, "There are no CVs"
    input_list = create_input_list(job_description, cvs)
    llm_chain = llm_chain_func()
    return llm_chain.apply(input_list)