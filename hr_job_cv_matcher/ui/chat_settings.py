from typing import List

import chainlit as cl
from chainlit.input_widget import Slider, TextInput
from hr_job_cv_matcher.service.candidate_ranking import DEFAULT_WEIGHTS

def create_chat_settings() -> List:
    return cl.ChatSettings(
        [
            Slider(
                id="matching_skills_weight",
                label="Matching skills weight",
                initial=DEFAULT_WEIGHTS.matching_skills_weight,
                min=0,
                max=4,
                step=0.1,
            ),
            Slider(
                id="missing_skills_weight",
                label="Missing skills weight",
                initial=DEFAULT_WEIGHTS.missing_skills_weight,
                min=-2,
                max=0,
                step=0.1,
            ),
            Slider(
                id="social_skills_weight",
                label="Social skills weight",
                initial=DEFAULT_WEIGHTS.social_skills_weight,
                min=0,
                max=4,
                step=0.1,
            ),
            Slider(
                id="relevant_job_list_weight",
                label="Relevant Job list weight",
                initial=DEFAULT_WEIGHTS.relevant_job_list_weight,
                min=0,
                max=4,
                step=0.1,
            ),
            Slider(
                id="relevant_degree_list_weight",
                label="Relevant degree list weight",
                initial=DEFAULT_WEIGHTS.relevant_degree_list_weight,
                min=0,
                max=4,
                step=0.1,
            ),
            Slider(
                id="years_of_experience_weight",
                label="Years of experience weight",
                initial=DEFAULT_WEIGHTS.years_of_experience_weight,
                min=0,
                max=4,
                step=0.1,
            ),
            TextInput(id="prompt_extra_skills_examples", label="Prompt extra skills examples (comma-separated)", initial=""),
        ]
    )