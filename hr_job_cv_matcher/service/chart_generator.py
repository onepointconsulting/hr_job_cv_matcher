import time
from pathlib import Path

from typing import List

import matplotlib.pyplot as plt

from hr_job_cv_matcher.model import CandidateProfile
from hr_job_cv_matcher.config import cfg

def generate_chart(sorted_candidate_profiles: List[CandidateProfile]) -> str:

    # Extract names and scores
    names = [Path(profile.source).stem for profile in sorted_candidate_profiles]
    scores = [profile.score for profile in sorted_candidate_profiles]

    # Sort data in descending order
    sorted_data = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)
    sorted_names, sorted_scores = zip(*sorted_data)

    # Create the ranking chart
    plt.figure(figsize=(12, 8))
    plt.barh(sorted_names, sorted_scores, color='blue')
    plt.xlabel('Scores')
    plt.ylabel('Names')
    plt.title('Ranking Chart')
    plt.gca().invert_yaxis()  # Invert y-axis to show highest score at the top

    time_millis = round(time.time() * 1000)

    ranking_plot = cfg.temp_doc_location / f"hr_job_cv_matcher_{time_millis}_ranking.png"
    plt.savefig(ranking_plot)
    return ranking_plot