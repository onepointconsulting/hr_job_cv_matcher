from pathlib import Path
from asyncer import asyncify
from hr_job_cv_matcher.list_utils import convert_list_to_markdown
from hr_job_cv_matcher.model import (
    CandidateProfile,
    EducationCareerJson,
    MatchSkillsProfileJson,
    ScoreWeightsJson,
)
from hr_job_cv_matcher.service.candidate_ranking import DEFAULT_WEIGHTS, calculate_score, sort_candidates
from hr_job_cv_matcher.service.document_matcher import (
    MatchSkillsProfile,
    create_input_list,
    create_match_profile_chain_pydantic,
)
from hr_job_cv_matcher.service.education_extraction import (
    create_education_chain,
)
from langchain.schema import Document
from typing import List, Dict, Tuple, Optional

import chainlit as cl
from chainlit.input_widget import Slider, Select, Switch

from hr_job_cv_matcher.document_factory import convert_to_doc

from hr_job_cv_matcher.log_init import logger
from hr_job_cv_matcher.config import cfg

TIMEOUT = 1200
LLM_AUTHOR = "LLM"
HR_ASSISTANT = "HR Assistant"

KEY_APPLICATION_DOCS = "application_docs"
KEY_CV_DOCS = "cv_docs"


@cl.on_chat_start
async def init():
    await cl.Message(
        content=f"**May the working force be with you.**",
    ).send()
    application_docs = await upload_and_extract_text("job description file")

    if application_docs is not None and len(application_docs) > 0:
        application_path = Path(application_docs[0].metadata["source"])
        elements = [
            cl.Pdf(
                name=application_path.name,
                display="inline",
                path=str(application_path.absolute()),
            )
        ]
        await cl.Message(
            content=f"Job description processed: {application_path.name}",
            elements=elements,
        ).send()

        cvs_docs = await upload_and_extract_text("CV files", max_files=cfg.max_cv_files)
        if cvs_docs is not None and len(cvs_docs) > 0:
            await display_scoring_sliders(application_docs, cvs_docs)

        else:
            await cl.ErrorMessage(
                content=f"Could not process the CVs. Please try again",
            ).send()
    else:
        await cl.ErrorMessage(
            content=f"Could not process the application document. Please try again",
        ).send()


@cl.on_settings_update
async def setup_agent(settings):
    logger.info("Settings: %s", settings)
    application_docs = cl.user_session.get(KEY_APPLICATION_DOCS)
    cvs_docs = cl.user_session.get(KEY_CV_DOCS)
    logger.info("application_docs: %s", len(application_docs))
    score_weights = ScoreWeightsJson.factory(settings=settings)
    candidate_profiles: List[CandidateProfile] = await process_applications_and_cvs(
        application_docs, cvs_docs, score_weights
    )
    sorted_candidate_profiles: List[CandidateProfile] = sort_candidates(candidate_profiles)
    await render_ranking(sorted_candidate_profiles)
    breakdown_msg_id = await cl.Message(content=f"### Breakdown").send()
    await render_breakdown(sorted_candidate_profiles, breakdown_msg_id)



async def render_ranking(sorted_candidate_profiles: List[CandidateProfile]):
    ranking_message = "## Ranking"
    for i, profile in enumerate(sorted_candidate_profiles):
        path = Path(profile.source)
        ranking_message += f"\n{i + 1}. {path.name}: **{profile.score}** points"
    await cl.Message(content=ranking_message, indent=0).send()



async def render_breakdown(sorted_candidate_profiles: List[CandidateProfile], breakdown_msg_id: str):
    for profile in sorted_candidate_profiles:
        skills = profile.matched_skills_profile
        await render_pdf(profile, breakdown_msg_id)
        if skills:
            msg_id = await render_scoring(skills, breakdown_msg_id)
            await render_skills(skills, msg_id=msg_id)
        education_career_profile = profile.education_career_profile
        if education_career_profile:
            await render_education(education_career_profile, breakdown_msg_id)
        if skills and education_career_profile:
            await render_score(profile, breakdown_msg_id)


async def process_applications_and_cvs(
    application_docs: List[Document],
    cvs_docs: List[Document],
    score_weights: ScoreWeightsJson,
) -> List[CandidateProfile]:
    await cl.Message(content=f"{len(cvs_docs)} CV(s) uploaded.").send()
    candidate_profiles: List[
        CandidateProfile
    ] = await process_job_description_and_candidates(application_docs[0], cvs_docs)
    scored_profiles = []
    if len(candidate_profiles) > 0:
        for profile in candidate_profiles:
            skills = profile.matched_skills_profile
            education_career_profile = profile.education_career_profile
            if skills and education_career_profile:
                score, breakdown = calculate_score(profile, score_weights)
                profile.score = score
                profile.breakdown = breakdown
                scored_profiles.append(profile)
    return candidate_profiles


async def upload_and_extract_text(
    item_to_upload: str, max_files: int = 1
) -> List[Document]:
    files = None
    application_docs: List[Document] = []
    while files is None:
        files = await cl.AskFileMessage(
            content=f"Please upload a {item_to_upload}!",
            accept=["application/pdf"],
            max_files=max_files,
            timeout=TIMEOUT,
        ).send()
        if files is not None:
            for file in files:
                logger.info(type(file))
                await cl.Message(
                    content=f"Processing {file.name}. Please wait ...",
                ).send()
                application_docs.append(await asyncify(convert_to_doc)(file=file))
                logger.info("Document: %s", application_docs)
    return application_docs


async def process_job_description_and_candidates(
    application_doc: Document, cv_documents: List[Document]
) -> List[CandidateProfile]:
    sources, input_list = extract_sources_input_list(application_doc, cv_documents)
    profile_llm_chain = create_match_profile_chain_pydantic()

    skill_results_msg, skill_results = await process_skills_llm_chain(input_list, profile_llm_chain)
    education_results = await process_career_llm_chain(input_list)

    extracted_profiles: List[CandidateProfile] = []
    if len(sources) == len(skill_results) == len(education_results):
        for source, skill_result, education_result in zip(
            sources, skill_results, education_results
        ):
            if "function" in skill_result:
                match_skills_profile: MatchSkillsProfile = skill_result["function"]
                logger.info("Matching skills: %a", match_skills_profile)
                # Process jobs
                education_career_dict: dict = education_result["function"]
                logger.info("Matching education: %a", education_career_dict)
                education_career_json = EducationCareerJson(
                    relevant_degree_list=education_career_dict["relevant_degree_list"],
                    relevant_job_list=education_career_dict["relevant_job_list"],
                    years_of_experience=education_career_dict["years_of_experience"],
                )
                extracted_profiles.append(
                    CandidateProfile(
                        source=source,
                        document=application_doc,
                        matched_skills_profile=MatchSkillsProfileJson(
                            matching_skills=match_skills_profile.matching_skills,
                            missing_skills=match_skills_profile.missing_skills,
                            social_skills=match_skills_profile.social_skills,
                            suitability_score=match_skills_profile.suitability_score,
                        ),
                        education_career_profile=education_career_json,
                        score=0,
                        breakdown="",
                    )
                )
        return extracted_profiles
    await cl.ErrorMessage(
        content=f"The number of sources and results is not the same",
    ).send()
    return None

async def process_career_llm_chain(input_list):
    
    education_llm_chain = create_education_chain()
    education_results_msg = cl.Message(
        content="",
        prompt=education_llm_chain.prompt.format(job_description="'job description'", cv="'CV'")
    )

    await education_results_msg.stream_token("Started career extraction. Please wait ...\n\n")
    education_results = await education_llm_chain.aapply_and_parse(
        input_list
    )
    await education_results_msg.stream_token("Finished career extraction\n\n")
    await education_results_msg.send()
    return education_results

async def process_skills_llm_chain(input_list, profile_llm_chain):
    skill_results_msg = cl.Message(
        content="",
        prompt=profile_llm_chain.prompt.format(job_description="'job description'", cv="'CV'")
    )
    await skill_results_msg.stream_token("Started skill extraction. Please wait ...\n\n")
    skill_results = await profile_llm_chain.aapply_and_parse(
        input_list
    )
    await skill_results_msg.stream_token("Finished skill extraction\n\n")
    await skill_results_msg.send()
    return skill_results_msg,skill_results


def extract_sources_input_list(
    application_doc, cv_documents
) -> Tuple[List[str], List[Dict]]:
    job_description = application_doc.page_content
    cvs = [c.page_content for c in cv_documents]
    sources = [c.metadata["source"] for c in cv_documents]
    input_list = create_input_list(job_description, cvs)
    return sources, input_list


async def render_skills(match_skills_profile: MatchSkillsProfileJson, msg_id: str):
    matching_skills = render_skills_str(
        "Matching Skills\n", match_skills_profile.matching_skills
    )
    await cl.Message(
        content=matching_skills, author=LLM_AUTHOR, parent_id=msg_id
    ).send()
    missing_skills = render_skills_str(
        "Missing Skills\n", match_skills_profile.missing_skills
    )
    await cl.Message(content=missing_skills, author=LLM_AUTHOR, parent_id=msg_id).send()
    social_skills = render_skills_str(
        "Social Skills\n", match_skills_profile.social_skills
    )
    await cl.Message(content=social_skills, author=LLM_AUTHOR, parent_id=msg_id).send()


async def render_education(education_career: EducationCareerJson, breakdown_msg_id: str):
    try:
        relevant_degree_list = education_career.relevant_degree_list
        degree_output = convert_list_to_markdown(relevant_degree_list)
        relevant_job_list = education_career.relevant_job_list
        job_output = convert_list_to_markdown(relevant_job_list)
        logger.info("years_of_experience: %s", education_career.years_of_experience)
        years_of_experience = (
            ""
            if education_career.years_of_experience is None
            else f"- Years of experience: {education_career.years_of_experience}"
        )

        if len(degree_output) > 0 or len(job_output) > 0:
            detailed_output = f"""
#### Degrees
{degree_output}
#### Jobs
{job_output}
"""
            summary = f"""
#### Experience:
- Relevant jobs: {len(relevant_job_list)}
- Relevant degrees: {len(relevant_degree_list)}
{years_of_experience}
"""
            msg_id = await cl.Message(content=summary, author=LLM_AUTHOR, parent_id=breakdown_msg_id).send()
            await cl.Message(
                content=detailed_output, author=LLM_AUTHOR, parent_id=msg_id
            ).send()
    except:
        logger.exception("Could not render education")


async def render_pdf(candidate_profile: CandidateProfile, breakdown_msg_id: str):
    source = candidate_profile.source
    path = Path(source)
    if path.exists():
        elements = [
            cl.Pdf(name=path.stem, display="inline", path=str(path.absolute()))
        ]
        await cl.Message(
            content=f"#### {path.name}", 
            author=HR_ASSISTANT, 
            parent_id=breakdown_msg_id,
            elements=elements
        ).send()


async def render_scoring(match_skills_profile: MatchSkillsProfileJson, breakdown_msg_id: str):
    matching_skills_count = len(match_skills_profile.matching_skills)
    missing_skills_count = len(match_skills_profile.missing_skills)
    social_skills_count = len(match_skills_profile.social_skills)
    message = f"""
#### Skills:
- Matching skills: {matching_skills_count}
- Missing skills: {missing_skills_count}
- Social skills: {social_skills_count}
"""
    return await cl.Message(content=message, author=LLM_AUTHOR, parent_id=breakdown_msg_id).send()


async def render_score(profile: CandidateProfile, breakdown_msg_id: str):
    message = f"""
#### Score:
- **{profile.score}**
- {profile.breakdown}
"""
    return await cl.Message(content=message, author=LLM_AUTHOR, parent_id=breakdown_msg_id).send()


def render_skills_str(title: str, skills: List[Dict]) -> str:
    matching_skill_str = f"### {title}"
    for matching_skill in skills:
        matching_skill_str += f"\n- {matching_skill}"
    return matching_skill_str



async def display_scoring_sliders(
    application_docs: List[Document], cvs_docs: List[Document]
):
    cl.user_session.set(KEY_APPLICATION_DOCS, application_docs)
    cl.user_session.set(KEY_CV_DOCS, cvs_docs)
    chat_settings = cl.ChatSettings(
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
        ]
    )
    res: Optional[dict] = None
    settings = None
    while True:
        res = await cl.AskUserMessage(
            content="Now you can change the weights via the settings button. Please type 'ok' to proceed.",
            timeout=TIMEOUT,
        ).send()
        if res is not None and "ok" in res["content"].lower():
            settings = await chat_settings.send()
            break
    await setup_agent(settings)
