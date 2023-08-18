import re
from typing import List
from pydantic import BaseModel, Field

from langchain import LLMChain
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain

from hr_job_cv_matcher.log_init import logger
from hr_job_cv_matcher.config import cfg, prompt_cfg


HR_SYSTEM_MESSAGE = "You are an expert in human resources and you are an expert at matching skills from a job description to a CV of a candidate"
JOB_DESCRIPTION_START = "=== 'JOB DESCRIPTION:' ==="
JOB_DESCRIPTION_END = "=== 'END JOB DESCRIPTION' ==="
CV_START = "=== CV START: ==="
CV_END = "=== CV END: ==="
JOB_DESCRIPTION_KEY='job_description'
PLACE_HOLDER_JOB_DESCRIPTION = f"{{{JOB_DESCRIPTION_KEY}}}"
PLACE_HOLDER_KEY = "cv"
PLACE_HOLDER_CV = f"{{{PLACE_HOLDER_KEY}}}"
HUMAN_MESSAGE_1 = f"""Please extract first the skills from the job description. 
The job description part starts with {JOB_DESCRIPTION_START} and ends with {JOB_DESCRIPTION_END}.
The CV (curriculum vitae of a candidate) description part starts with {CV_START} and ends with {CV_END}. Then output the matching, missing and associated skills using the provided JSON structure.

Here are some examples of skills that you might find in the job descriptions and CVs:
- Wordpress
- Creating Wordpress websites
- Website Optimization
- PHP
- SQL
- Javascript
- Debugging
- HTML
- HTML5
- CSS
- CSS3
- WOO-Commerce Management
- Client Support
- Python 
- Linux, macOS, and Windows
- Git
- Building E-commerce stores using woocmmerce plugin
- Front-end development
- Codeigniter
- Programming languages: C, C++
- Machine Learning
- Deep Learning
- Database: MySQL
- Database: MongoDB
- IDEs: IntelliJ
- Azure Logic apps
- Azure Data Factor
- Azure Functions
- Experience with REST APIs
- Experience with Business Intelligence BI
- Analytical reporting using PowerBI
- Exposure to ITIL
{{extra_skills}}


"""
HUMAN_MESSAGE_JD = f"""{JOB_DESCRIPTION_START}
{PLACE_HOLDER_JOB_DESCRIPTION}
{JOB_DESCRIPTION_END}
"""
HUMAN_MESSAGE_CV = f"""{CV_START}
{PLACE_HOLDER_CV}
{CV_END}
"""
TIPS_PROMPT = "Tips: Make sure you answer in the right format"


class MatchSkillsProfile(BaseModel):
    """Contains the information on how a candidate matched the profile."""

    matching_skills: List[str] = Field(..., description="The list of skills of the candidate which matched the skills in the job description.")
    missing_skills: List[str] = Field(..., description="The list of skills that are in the job description, but not matched in the job profile.")
    social_skills: List[str] = Field(..., description="A list of skills which are mentioned in the candidate CV only.")


json_schema_match_skills = {
    "title": "MatchingSkills",
    "description": "Collects matching and missing skills between a candidate's CV and a job application",
    "type": "object",
    "properties": {
        "matching_skills": {
            "title": "Matching skills list",
            "description": "The list of skills of the candidate which matched the skills in the job description.",
            "type": "array",
            "items": {"type": "string"},
        },
        "missing_skills": {
            "title": "Missing skills list",
            "description": "The list of skills that are in the job description, but not matched in the job profile.",
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["matching_skills", "missing_skills"],
}


def prompt_factory(system_message: str, human_messages: List[str]) -> ChatPromptTemplate:
    assert len(human_messages) > 0, "The human messages cannot be empty"
    final_human_messages = []
    count_template = 0
    regex = re.compile(r"\{[^}]+\}", re.MULTILINE)
    for m in human_messages:
        if re.search(regex, m):
            # In case there is a placeholder
            final_human_messages.append(HumanMessagePromptTemplate.from_template(m))
            count_template += 1
        else:
            # No placeholder
            final_human_messages.append(HumanMessage(content=m))
    assert count_template > 0, "There has to be at least one human message with {}"
    logger.info("Template count: %d", count_template)
    prompt_msgs = [
        SystemMessage(
            content=system_message
        ),
        *final_human_messages
    ]
    return ChatPromptTemplate(messages=prompt_msgs)


def create_zero_shot_matching_prompt() -> ChatPromptTemplate:
    system_message = HR_SYSTEM_MESSAGE
    human_message_1 = HUMAN_MESSAGE_1.format(extra_skills=prompt_cfg.extra_skills)
    logger.info("human_message_1: %s", human_message_1)
    return prompt_factory(system_message, [human_message_1, HUMAN_MESSAGE_JD, HUMAN_MESSAGE_CV, TIPS_PROMPT])


def create_match_profile_chain_pydantic() -> LLMChain:
    return create_structured_output_chain(MatchSkillsProfile, cfg.llm, create_zero_shot_matching_prompt(), verbose=cfg.verbose_llm)


def create_match_profile_chain() -> LLMChain:
    return create_structured_output_chain(json_schema_match_skills, cfg.llm, create_zero_shot_matching_prompt(), verbose=cfg.verbose_llm)


def create_input_list(job_description, cvs):
    return [{JOB_DESCRIPTION_KEY: job_description, PLACE_HOLDER_KEY: cv} for cv in cvs]

