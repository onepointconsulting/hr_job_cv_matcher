import json
from typing import List

from dataclasses import dataclass
from langchain.schema import Document

from hr_job_cv_matcher.service.document_matcher import MatchSkillsProfile
from hr_job_cv_matcher.service.education_extraction import EducationCareer
from hr_job_cv_matcher.log_init import logger



class MatchSkillsProfileJson(dict):
    matching_skills: List[str]
    missing_skills: List[str]
    social_skills: List[str]

    def __init__(self, matching_skills: List[str], missing_skills: List[str], social_skills: List[str]) -> None:
        self.matching_skills = matching_skills
        self.missing_skills = missing_skills
        self.social_skills = social_skills
        dict.__init__(
            self,
            matching_skills=self.matching_skills,
            missing_skills=self.missing_skills,
            social_skills=self.social_skills,
        )

    @classmethod
    def factory(cls, result: dict):
        if 'function' in result:
            content = result['function']
            matching_skills = content['matching_skills']
            missing_skills = content['missing_skills']
            social_skills = content['social_skills']
            return cls(matching_skills, missing_skills, social_skills)
        logger.warn("Cannot parse dict: %s", result)
        return None


class EducationCareerJson(dict):
    relevant_job_list: List[str]
    relevant_degree_list: List[str]
    years_of_experience: int

    def __init__(
        self, relevant_job_list, relevant_degree_list, years_of_experience
    ) -> None:
        self.relevant_job_list = relevant_job_list
        self.relevant_degree_list = relevant_degree_list
        self.years_of_experience = years_of_experience
        dict.__init__(
            self,
            relevant_job_list=self.relevant_job_list,
            relevant_degree_list=self.relevant_degree_list,
            years_of_experience=self.years_of_experience,
        )


class ScoreWeightsJson(dict):
    matching_skills_weight: float
    missing_skills_weight: float
    social_skills_weight: float
    relevant_job_list_weight: float
    relevant_degree_list_weight: float
    years_of_experience_weight: float

    def __init__(
        self,
        matching_skills_weight,
        missing_skills_weight,
        social_skills_weight,
        relevant_job_list_weight,
        relevant_degree_list_weight,
        years_of_experience_weight,
    ) -> None:
        self.matching_skills_weight, self.missing_skills_weight = (
            matching_skills_weight,
            missing_skills_weight,
        )
        self.social_skills_weight, self.relevant_job_list_weight = (
            social_skills_weight,
            relevant_job_list_weight,
        )
        self.relevant_degree_list_weight, self.years_of_experience_weight = (
            relevant_degree_list_weight,
            years_of_experience_weight,
        )
        dict.__init__(
            self,
            matching_skills_weight=self.matching_skills_weight,
            missing_skills_weight=self.missing_skills_weight,
            social_skills_weight=self.social_skills_weight,
            relevant_job_list_weight=self.relevant_job_list_weight,
            relevant_degree_list_weight=self.relevant_degree_list_weight,
            years_of_experience_weight=self.years_of_experience_weight,
        )

    @classmethod
    def factory(cls, settings: dict):
        return cls(
            matching_skills_weight=settings['matching_skills_weight'],
            missing_skills_weight=settings['missing_skills_weight'],
            relevant_degree_list_weight=settings['missing_skills_weight'],
            relevant_job_list_weight=settings['relevant_job_list_weight'],
            social_skills_weight=settings['social_skills_weight'],
            years_of_experience_weight=settings['years_of_experience_weight']
        )


@dataclass
class CandidateProfile:
    """Class which contains all profile elements for a specific candidate based on a job description"""

    source: str
    document: Document
    matched_skills_profile: MatchSkillsProfileJson
    education_career_profile: EducationCareerJson
    score: float
    breakdown: str

if __name__ == "__main__":
    match_skills_profile = MatchSkillsProfile(
        matching_skills=["test"],
        missing_skills=["test1"],
        social_skills=["test_social"],
    )
    match_skills = MatchSkillsProfileJson(
        matching_skills=match_skills_profile.matching_skills, 
        missing_skills=match_skills_profile.missing_skills,
        social_skills=match_skills_profile.social_skills
    )
    print(json.dumps(match_skills))
    education_career = EducationCareerJson(
        relevant_job_list=["test"],
        relevant_degree_list=["test"],
        years_of_experience=3
    )
    print(json.dumps(education_career))
