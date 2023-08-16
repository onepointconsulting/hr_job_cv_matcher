from typing import Tuple, List

from hr_job_cv_matcher.model import CandidateProfile, ScoreWeightsJson
from hr_job_cv_matcher.service.test.candidate_profile_provider import create_candidate_profile


DEFAULT_WEIGHTS = ScoreWeightsJson(2, -1, 0.5, 1, 1, 0.5)

def calculate_score(candidate_profile: CandidateProfile, weights: ScoreWeightsJson=DEFAULT_WEIGHTS) -> Tuple[int, str]:
    skills_profile = candidate_profile.matched_skills_profile
    matched_skills_count = len(skills_profile.matching_skills)
    missed_skills_count = len(skills_profile.missing_skills)
    social_skills_count = len(skills_profile.social_skills)
    career_profile = candidate_profile.education_career_profile
    degree_count = len(career_profile.relevant_degree_list)
    job_count = len(career_profile.relevant_job_list)
    years_of_experience = 0 if career_profile.years_of_experience is None else career_profile.years_of_experience
    score = (
        matched_skills_count * weights.matching_skills_weight + 
        missed_skills_count * weights.missing_skills_weight +
        social_skills_count * weights.social_skills_weight + 
        degree_count * weights.relevant_degree_list_weight +
        job_count * weights.relevant_job_list_weight + 
        years_of_experience * weights.years_of_experience_weight
    )
    breakdown = (f"{score} = {matched_skills_count} * {weights.matching_skills_weight} + " + 
        f"{missed_skills_count} * {weights.missing_skills_weight} + " + 
        f"{social_skills_count} * {weights.social_skills_weight} + " +
        f"{degree_count} * {weights.social_skills_weight} + " +
        f"{job_count} * {weights.relevant_job_list_weight} + " +
        f"{years_of_experience} * {weights.years_of_experience_weight}"
    )
    return (score, breakdown)


def sort_candidates(candidate_profiles: List[CandidateProfile]) -> List[CandidateProfile]:
    return sorted(candidate_profiles, key=lambda x: x.score, reverse=True)


if __name__ == "__main__":
    from hr_job_cv_matcher.log_init import logger
    candidate_profile = create_candidate_profile()
    score, breakdown = calculate_score(candidate_profile)
    logger.info("Score: %d", score)
    logger.info("Breakdown: %s", breakdown)
