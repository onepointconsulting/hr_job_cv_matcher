import requests

from hr_job_cv_matcher.config import cfg
from hr_job_cv_matcher.log_init import logger


CV = f"""Proficient and creative WordPress developer with a 2+ years of experience in 
software development. I have worked on back-end management systems 
including content management and e-commerce. The projects based on PHP 
in conjunction. Skilled in creating engaging and interactive websites. Excel at 
team projects and leadership. Detail-oriented and knowledgeable in various
programming languages. Dedicated to superior customer service at all
levels from the first meeting with a client to the website maintenance after
launch.

Work Experience
SculptSoft, Ahmedabad | March 2023 – Present
Web Designer
➔ Developing and maintaining the front-end functionality of websites.
➔ Wordpress site building using page builders like Beaver builder, Elementor, WP Bakery, etc
➔ Skilled In front-end development.
➔ Work Closely with SEO Team
Fantastech Solution, Pune | Sep 2020 – Jan 23
Wordpress Developer
➔ Creating Wordpress websites by making theme customization
➔ Wordpress site building using page builders like Beaver builder, Elementor, WP Bakery, etc
➔ Built E-commerce stores using woocmmerce plugin
➔ Writing clean and reusable code with cross browser compatibility
➔ Skilled In front-end development.
➔ Creating attractive and user-friendly websites.
➔ few Major Project :
1. https://www.stwhospice.org/
2. https://www.each.org.uk/
3. https://lillefolk.com/ - Ecommerce website
4. https://www.raleon.io/
5. https://fullhouse.io/
6. https://www.cyclopsmarine.com/
7. https://www.stgilestrust.org.uk/
cloudtrains technology, Pune | May 2019 – January 2020
Internship - Web Developer/Designer
Responsible for working on a range of project, designing appealing website and interacting on a
daily basis with graphics designer and digital marketing team.
➔ Developing and maintaining the front-end functionality of websites.
➔ Provides the Guidance to other team member on web development issue.
➔ Simultaneously managing back-end functionality of website.
➔ Participating in discussing with client to clarify what they want.

Education
Bachelor of Technology in Computer Science Engineering 
Cochin University of Science & Technology
2010-2014
Higher Secondary 
GHSS Ramapuram 2007-09
Secondary
Bethany Balikamadom High School 2006-07
ACADEMIC CERTIFICATIONS 
Acquired Bachelor’s Degree in Computer Science Engineering 
Papers in Software Engineering and Digital Communication
Complimentary Papers in Electrical and Electronics 
Successfully Completed 6 months internship at in PHP Technology 
from KELTRON
Completed One month Internship and one month training in software 
testing.

"""

def job_description_cv_provider():
    job_description = f"""Onepoint Consulting is looking for a Wordpress developer that will look after multiple websites. The candidate's responsibilities are:
    - updating the content of the websites
    - Changing the design
    - Maintaining and adding Wordpress plugins
    - Eventually extending existing plugins using HTML, CSS and PHP
    - The candidate will be able to run a small team of web developers
    - Capacicty for managing SCRUM sessions
    """
    
    cvs = [CV]
    return job_description, cvs


def app_support_analyst_provider():
    return job_description_cv_provider_query('PUNE_JD2023-02_IN.007-App-Support-Analyst.pdf')


def web_developer_provider():
    return job_description_cv_provider_query('CutShort-resume-l6CL.pdf')



def job_description_cv_provider_2():
    job_description = app_support_analyst_provider()
    cvs = [web_developer_provider()]
    return job_description, cvs

def job_description_cv_provider_query(file_name: str) -> str:
    remote_pdf_server = cfg.remote_pdf_server.replace("/upload", "")
    resume_res = requests.get(f"{remote_pdf_server}/cached_file/{file_name}")
    resume_json = resume_res.json()
    if 'code' in resume_json and resume_json['code'] == 'OK':
        logger.info("Request successful")
        if 'extracted_text' in resume_json:
            return resume_json['extracted_text']
    else:
        logger.info("Request res: %s", dir(resume_json))



if __name__ == "__main__":
    res = app_support_analyst_provider()
    lines = res.split("\n")
    for line in lines:
        if "itil" in line.lower():
            logger.info(line)
    res = web_developer_provider()
    logger.info("\n".join(res.split("\n")[:8]))