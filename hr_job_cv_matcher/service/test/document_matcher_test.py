from hr_job_cv_matcher.log_init import logger
from hr_job_cv_matcher.model import MatchSkillsProfileJson
from hr_job_cv_matcher.service.cv_processing import process_multiple_cvs
from hr_job_cv_matcher.service.job_description_cv_matcher import create_match_profile_chain
from hr_job_cv_matcher.service.education_extraction import create_education_chain, create_education_chain_pydantic
from hr_job_cv_matcher.service.test.job_description_cv_provider import job_description_cv_provider, job_description_cv_provider_2


def test_create_match_profile_chain():
    job_description, cvs = job_description_cv_provider_2()
    result = process_multiple_cvs(job_description, cvs, create_match_profile_chain)
    logger.info(type(result))
    logger.info(type(result[0]))
    logger.info(type(result[0]['function']))
    logger.info(result)
    match_skills_profile = MatchSkillsProfileJson.factory(result[0])
    assert match_skills_profile is not None
    logger.info("Matching skills: %s", match_skills_profile.matching_skills)



def test_education_extraction(chain_func=create_education_chain):
    job_description, cvs = job_description_cv_provider()
    result = process_multiple_cvs(job_description, cvs, chain_func)
    logger.info(result)
    logger.info(type(result[0]['function']))



if __name__ == "__main__":
    test_create_match_profile_chain()
    logger.info(" ############################ ")
    # test_education_extraction()
    # logger.info(" ############################ ")
    # test_education_extraction(create_education_chain_pydantic)
    