import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3
import json
import secrets
import datetime
import re
import logging
import random

from numpy import var
app = Flask(__name__)
# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Setup ---
DB_NAME = "career_coach.db"
USER_CONTEXT = {}  # In-memory store for conversation context: session_id -> {'data': dict, 'history_summary': str}

# Enhanced Career Data with Tech and Non-Tech Roles
CAREER_PATHS = {
    "software_engineer": {
        "name": "Software Engineer",
        "keywords": ["software engineer", "developer", "coder", "programmer", "swe", "backend developer",
                     "frontend developer", "full stack developer"],
        "responsibilities_summary": "Designs, develops, tests, and maintains software applications. Collaborates with teams to build scalable and efficient solutions across various platforms.",
        "required_skills": ["python", "java", "javascript", "c++", "c#", "ruby", "go", "data_structures", "algorithms",
                            "git", "problem_solving", "api_design", "testing", "debugging", "agile_methodologies",
                            "system_design"],
        "soft_skills_emphasis": ["teamwork", "communication", "analytical_thinking", "adaptability",
                                 "continuous_learning"],
        "avg_salary_range": "$90,000 - $170,000 USD",
        "common_next_steps": ["senior_software_engineer", "tech_lead", "engineering_manager", "solutions_architect",
                              "principal_engineer"],
        "learning_resources": {
            "foundational": "CS50 (Harvard), freeCodeCamp (Full Stack Path), The Odin Project",
            "python": "Official Python Docs, Real Python, 'Python Crash Course' (book)",
            "java": "Oracle Java Tutorials, Udemy: Java Programming Masterclass, 'Head First Java' (book)",
            "javascript": "MDN Web Docs, Eloquent JavaScript (book), Traversy Media (YouTube), Frontend Masters",
            "data_structures_algorithms": "LeetCode, HackerRank, 'Cracking the Coding Interview' (book), 'Introduction to Algorithms' (CLRS)",
            "git": "Pro Git (book), Atlassian Git Tutorial, GitHub Learning Lab",
            "api_design": "REST API Design Rulebook (O'Reilly), Google API Design Guide, Postman Learning Center",
            "testing": "pytest docs, JUnit docs, Jest/Mocha docs, 'Software Testing' (Ron Patton), Kent C. Dodds (Testing JavaScript)",
            "agile": "Scrum Guide, Atlassian Agile Coach, 'Agile Estimating and Planning' (Mike Cohn)"
        },
        "interview_focus": ["Live coding (algorithms, data structures)", "System design (scalability, trade-offs)",
                            "Behavioral questions (STAR method)", "Debugging scenarios",
                            "Knowledge of specific tech stack"],
        "example_projects": ["Develop a full-stack web application (e.g., e-commerce site, social media clone)",
                             "Build a mobile app (iOS or Android)", "Contribute to an open-source project",
                             "Create a command-line tool with complex logic", "Develop a browser extension"]
    },
    "data_scientist": {
        "name": "Data Scientist",
        "keywords": ["data scientist", "data analyst", "machine learning engineer", "ai specialist",
                     "quantitative analyst"],
        "responsibilities_summary": "Collects, analyzes, and interprets large datasets to identify trends and insights. Develops machine learning models, designs experiments, and communicates findings to stakeholders to drive decision-making.",
        "required_skills": ["python", "r", "sql", "machine_learning", "deep_learning", "statistics", "probability",
                            "data_visualization", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
                            "communication", "big_data_technologies", "experiment_design"],
        "soft_skills_emphasis": ["critical_thinking", "problem_solving", "storytelling_with_data", "curiosity",
                                 "business_acumen"],
        "avg_salary_range": "$100,000 - $190,000 USD",
        "common_next_steps": ["senior_data_scientist", "lead_data_scientist", "ml_ops_engineer", "ai_researcher",
                              "analytics_manager", "head_of_data_science"],
        "learning_resources": {
            "foundational": "Coursera: Machine Learning (Andrew Ng), Kaggle Learn, DataCamp/DataQuest",
            "python_for_ds": "'Python for Data Analysis' (Wes McKinney), 'Applied Text Analysis with Python' (Benjamin Bengfort et al.)",
            "r": "R for Data Science (book/website), Swirl (interactive R package)",
            "sql": "SQLZoo, Mode Analytics SQL Tutorial, LeetCode SQL, 'SQL for Data Scientists' (Renee Teate)",
            "machine_learning": "fast.ai, 'Hands-On Machine Learning' (Aurélien Géron), Stanford CS229",
            "statistics": "Khan Academy Statistics, StatQuest (YouTube), 'The Elements of Statistical Learning' (book), MIT OpenCourseware Statistics",
            "data_visualization": "Tableau Public, Seaborn/Matplotlib docs, 'Storytelling with Data' (Cole Knaflic), D3.js tutorials"
        },
        "interview_focus": ["Statistical concepts and probability",
                            "ML model intuition, implementation, and evaluation",
                            "Data wrangling and cleaning (Python/R/SQL)", "Case studies and product sense",
                            "Communicating complex results simply", "A/B testing and experimental design"],
        "example_projects": ["Analyze a public dataset to uncover novel insights (e.g., Kaggle competition)",
                             "Build a predictive model for a specific business problem (e.g., churn, fraud)",
                             "Create an interactive data dashboard (e.g., using Plotly Dash, R Shiny, Tableau)",
                             "Develop a recommendation system", "Perform causal inference analysis"]
    },
    "product_manager": {
        "name": "Product Manager",
        "keywords": ["product manager", "pm", "product owner", "technical product manager"],
        "responsibilities_summary": "Defines product vision, strategy, and roadmap. Works with cross-functional teams (engineering, design, marketing, sales) to build, launch, and iterate on successful products that meet user needs and business goals.",
        "required_skills": ["market_research", "user_research", "user_experience_design_principles",
                            "agile_methodologies", "scrum", "communication", "leadership", "data_analysis",
                            "product_strategy", "stakeholder_management", "prioritization", "roadmapping",
                            "a_b_testing_analysis", "product_analytics_tools"],
        "soft_skills_emphasis": ["empathy", "strategic_thinking", "influence_without_authority", "decisiveness",
                                 "collaboration", "storytelling"],
        "avg_salary_range": "$115,000 - $220,000 USD",
        "common_next_steps": ["senior_product_manager", "group_product_manager", "director_of_product", "vp_of_product",
                              "entrepreneur", "product_lead"],
        "learning_resources": {
            "foundational": "Product School, 'Inspired' (Marty Cagan), 'Cracking the PM Interview' (Gayle McDowell), 'The Lean Product Playbook' (Dan Olsen)",
            "market_research": "HubSpot Market Research Guide, Nielsen Norman Group (user research articles)",
            "ux_principles": "'Don't Make Me Think' (Steve Krug), Laws of UX (website), 'About Face' (Alan Cooper)",
            "agile_pm": "Aha! Academy, 'User Story Mapping' (Jeff Patton), Scrum.org resources",
            "data_analysis_for_pm": "Amplitude blog, Mixpanel resources, basic SQL/Excel skills, Reforge programs",
            "strategy": "Stratechery (Ben Thompson blog), 'Good Strategy Bad Strategy' (Richard Rumelt), Harvard Business Review"
        },
        "interview_focus": ["Product sense (e.g., 'Design X for Y', 'Improve Z', 'Favorite product and why')",
                            "Behavioral questions (leadership, collaboration, conflict resolution)",
                            "Estimation and prioritization questions",
                            "Analytical and strategic thinking (market sizing, competitive analysis)",
                            "Technical understanding (for tech PM roles)"],
        "example_projects": ["Develop a detailed product requirements document (PRD) or user stories for a new feature",
                             "Conduct user interviews and synthesize findings into actionable insights",
                             "Create a competitive analysis report for a product category",
                             "Mockup a user flow and wireframes for a mobile app feature",
                             "Define and track key product metrics (KPIs)"]
    },
    "ux_ui_designer": {
        "name": "UX/UI Designer",
        "keywords": ["ux designer", "ui designer", "product designer", "interaction designer", "visual designer",
                     "user experience designer", "user interface designer"],
        "responsibilities_summary": "Focuses on creating user-centered designs by understanding business requirements, user needs, and technical limitations. Develops wireframes, prototypes, and high-fidelity visual designs for websites, apps, and other digital products.",
        "required_skills": ["user_research_methods", "wireframing", "prototyping", "information_architecture",
                            "interaction_design", "visual_design", "typography", "color_theory", "figma", "sketch",
                            "adobe_xd", "usability_testing", "user_personas_journey_mapping"],
        "soft_skills_emphasis": ["empathy", "communication", "collaboration", "problem_solving", "attention_to_detail",
                                 "creativity", "receptiveness_to_feedback"],
        "avg_salary_range": "$70,000 - $150,000 USD",
        "common_next_steps": ["senior_ux_ui_designer", "lead_product_designer", "design_manager", "ux_researcher",
                              "creative_director"],
        "learning_resources": {
            "foundational": "Nielsen Norman Group articles, Interaction Design Foundation (IDF) courses, Google UX Design Professional Certificate (Coursera)",
            "ux_principles": "'The Design of Everyday Things' (Don Norman), 'Don't Make Me Think' (Steve Krug)",
            "ui_visual_design": "'Refactoring UI' (Adam Wathan & Steve Schoger), Material Design Guidelines, Apple Human Interface Guidelines, Dribbble/Behance for inspiration",
            "tools": "Figma Learn, Sketch App Tutorials, Adobe XD Tutorials",
            "portfolio_building": "Bestfolios.com, 'Steal Like an Artist' (Austin Kleon)"
        },
        "interview_focus": ["Portfolio review (showcasing process and impact)",
                            "Design thinking and problem-solving approach", "Whiteboard design challenges",
                            "Explaining design decisions and rationale", "Collaboration and communication skills"],
        "example_projects": ["Redesign an existing website or app with a focus on usability improvements",
                             "Design a new mobile application from concept to high-fidelity prototype",
                             "Conduct user research and create user personas and journey maps for a product",
                             "Develop a design system or UI kit",
                             "Create a detailed case study for each portfolio piece explaining the problem, process, and solution."]
    },
    "digital_marketing_specialist": {
        "name": "Digital Marketing Specialist",
        "keywords": ["digital marketing", "seo specialist", "sem specialist", "social media manager",
                     "content marketer", "ppc analyst", "email marketing specialist"],
        "responsibilities_summary": "Develops, implements, and manages marketing campaigns that promote a company and its products or services. Enhances brand awareness, drives web traffic, and acquires leads/customers through various digital channels like SEO, SEM, social media, and email.",
        "required_skills": ["seo_principles_tools", "sem_ppc_platforms", "social_media_marketing_strategy",
                            "email_marketing_automation", "content_creation_strategy",
                            "data_analysis_marketing_metrics", "google_analytics", "marketing_automation_software",
                            "copywriting_for_web", "basic_graphic_design_video_editing"],
        "soft_skills_emphasis": ["creativity", "analytical_thinking", "communication", "adaptability",
                                 "project_management", "customer_empathy"],
        "avg_salary_range": "$60,000 - $110,000 USD",
        "common_next_steps": ["marketing_manager", "seo_manager", "digital_marketing_strategist", "head_of_marketing",
                              "growth_hacker"],
        "learning_resources": {
            "foundational": "Google Digital Garage (Fundamentals of Digital Marketing), HubSpot Academy (Inbound Marketing, Content Marketing), Coursera/Udemy courses on Digital Marketing",
            "seo": "Moz Blog, Ahrefs Blog, Google Search Central, Backlinko",
            "sem_ppc": "Google Ads Certification, WordStream PPC University, SEMrush Academy",
            "social_media": "Hootsuite Academy, Sprout Social Blog, Facebook Blueprint, Buffer Blog",
            "analytics": "Google Analytics Academy, CXL Institute (courses), Supermetrics Blog",
            "email_marketing": "Mailchimp Academy, Campaign Monitor Blog, Litmus Blog"
        },
        "interview_focus": ["Campaign strategy and execution examples",
                            "Knowledge of digital marketing tools and platforms (e.g., Google Ads, Facebook Ads Manager, GA4)",
                            "Analytical skills (interpreting data, ROI calculation, A/B testing)",
                            "Case studies on improving specific metrics (e.g., conversion rate, traffic)",
                            "Understanding of current digital marketing trends and algorithm changes"],
        "example_projects": ["Develop a comprehensive SEO audit and strategy for a small business website",
                             "Create and present a mock social media campaign strategy for a product launch",
                             "Analyze a marketing dataset to provide actionable insights and recommendations",
                             "Write sample ad copy for different platforms and target audiences",
                             "Outline an email marketing nurture sequence"]
    },
    "human_resources_manager": {
        "name": "Human Resources Manager",
        "keywords": ["hr manager", "human resources generalist", "talent acquisition manager", "hr business partner",
                     "people operations manager"],
        "responsibilities_summary": "Oversees recruitment and onboarding, employee relations, performance management, compensation and benefits administration, training and development programs, and ensures compliance with labor laws and company policies.",
        "required_skills": ["recruitment_and_staffing_strategies", "employee_relations_conflict_resolution",
                            "performance_management_systems", "compensation_and_benefits_design_administration",
                            "employment_law_compliance_knowledge", "hris_human_resources_information_systems",
                            "training_and_development_program_design", "change_management"],
        "soft_skills_emphasis": ["communication_active_listening", "interpersonal_skills_relationship_building",
                                 "empathy_emotional_intelligence", "problem_solving_decision_making",
                                 "confidentiality_discretion", "leadership_influence",
                                 "organizational_skills_time_management"],
        "avg_salary_range": "$75,000 - $150,000 USD",
        "common_next_steps": ["senior_hr_manager", "hr_director", "vp_of_hr", "chief_people_officer", "hr_consultant",
                              "organizational_development_specialist"],
        "learning_resources": {
            "foundational": "SHRM Certification (SHRM-CP, SHRM-SCP), HRCI Certifications (PHR, SPHR), University HR programs or degrees",
            "employment_law": "SHRM resources on compliance, Department of Labor website (country-specific), Legal updates from HR publications",
            "recruitment": "LinkedIn Talent Blog, ERE.net, SHRM Talent Acquisition resources",
            "employee_relations": "Books on conflict resolution and workplace mediation, Courses on difficult conversations",
            "hr_technology": "HR Technologist magazine, Reviews of HRIS platforms (e.g., BambooHR, Workday)"
        },
        "interview_focus": [
            "Scenario-based questions (handling employee issues, ethical dilemmas, legal compliance challenges)",
            "Experience with various HR processes and systems (e.g., ATS, performance review software)",
            "Leadership philosophy and management style", "Knowledge of current labor laws and HR best practices",
            "Behavioral questions focused on empathy, fairness, and strategic problem-solving"],
        "example_projects": ["Develop a proposal for a new employee wellness program",
                             "Outline a strategy to improve employee retention by X%",
                             "Create a training module for new managers on performance feedback",
                             "Draft an updated employee handbook section on remote work policies",
                             "Analyze HR metrics (e.g., turnover rate, time-to-hire) and suggest improvements"]
    },
    "graphic_designer": {
        "name": "Graphic Designer",
        "keywords": ["graphic artist", "visual designer", "brand designer", "communication_designer"],
        "responsibilities_summary": "Creates visual concepts using computer software or by hand to communicate ideas that inspire, inform, and captivate consumers. Develops layouts and production designs for advertisements, brochures, websites, corporate reports, and other media.",
        "required_skills": ["adobe_creative_suite_photoshop_illustrator_indesign", "typography_principles_application",
                            "color_theory_psychology", "layout_composition_hierarchy", "visual_communication_strategy",
                            "branding_identity_design", "illustration_skills", "digital_design_for_web_social",
                            "print_production_knowledge", "user_interface_design_basics_optional"],
        "soft_skills_emphasis": ["creativity_innovation", "attention_to_detail_precision",
                                 "communication_articulating_design_choices", "time_management_meeting_deadlines",
                                 "ability_to_take_and_give_constructive_criticism", "problem_solving_visual_challenges",
                                 "adaptability_to_different_styles_media"],
        "avg_salary_range": "$50,000 - $95,000 USD",
        "common_next_steps": ["senior_graphic_designer", "art_director", "creative_director",
                              "ux_designer_with_visual_focus", "freelance_design_business_owner", "brand_strategist"],
        "learning_resources": {
            "foundational": "Design school programs (BFA/MFA), Coursera/Skillshare/Udemy courses on Graphic Design, Books like 'Thinking with Type' (Ellen Lupton), 'Grid Systems in Graphic Design' (Josef Müller-Brockmann)",
            "adobe_suite": "Adobe Creative Cloud Learn & Support, YouTube channels (e.g., Phlearn, Dansky, Satori Graphics)",
            "typography": "Typewolf website, Fonts In Use, 'The Elements of Typographic Style' (Robert Bringhurst)",
            "design_principles_inspiration": "Smashing Magazine, Designmodo, Dribbble, Behance, Awwwards",
            "branding": "'Designing Brand Identity' (Alina Wheeler), Marty Neumeier books ('The Brand Gap', 'Zag')"
        },
        "interview_focus": ["Portfolio review (demonstrating range, skill, and thought process - most critical part)",
                            "Explanation of design process and rationale behind specific design choices",
                            "Understanding of fundamental design principles (balance, contrast, hierarchy etc.)",
                            "Software proficiency (Adobe CC, Figma etc.)",
                            "Ability to articulate design decisions, collaborate, and respond to feedback constructively"],
        "example_projects": [
            "Complete branding package for a fictional company (logo, color palette, typography, mockups)",
            "Website or mobile app UI design project (showcasing user flow and visual design)",
            "Editorial design for a magazine spread or book cover", "Social media campaign visuals",
            "Packaging design concept"]
    },
    "teacher_educator": {
        "name": "Teacher / Educator",
        "keywords": ["teacher", "educator", "instructor", "professor", "k-12 teacher", "higher education faculty",
                     "corporate trainer", "instructional designer"],
        "responsibilities_summary": "Plans, prepares, and delivers instructional activities that facilitate active learning experiences. Develops curriculum, assesses student performance, and creates a supportive and engaging learning environment across various settings (K-12, higher ed, corporate).",
        "required_skills": ["curriculum_development", "instructional_design_models_addiem",
                            "classroom_management_or_training_facilitation", "assessment_and_evaluation_methods",
                            "subject_matter_expertise", "differentiated_instruction_or_adult_learning_principles",
                            "educational_technology_integration_lms",
                            "communication_with_students_parents_colleagues_stakeholders",
                            "learning_theories_pedagogy_andragogy"],
        "soft_skills_emphasis": ["patience", "empathy", "communication_public_speaking", "adaptability_flexibility",
                                 "passion_for_learning_and_teaching", "organizational_skills_planning",
                                 "leadership_facilitation_skills", "creativity_in_instruction"],
        "avg_salary_range": "$45,000 - $95,000 USD (K-12/Corp Training, varies greatly), $60,000 - $150,000+ (Higher Ed)",
        "common_next_steps": ["lead_teacher_trainer", "department_head", "instructional_coordinator_designer",
                              "school_administrator_principal_training_manager", "curriculum_specialist_developer",
                              "educational_consultant", "university_tenure_track_professor"],
        "learning_resources": {
            "foundational": "Teacher certification programs (state-specific for K-12), Master's/Doctorate in Education or specific subject area, ATD (Association for Talent Development) for corporate trainers.",
            "pedagogy_andragogy": "Journals like 'Educational Leadership', Books by authors like Parker Palmer, Bell Hooks, Malcolm Knowles, 'Understanding by Design' (Wiggins & McTighe)",
            "classroom_management_facilitation": "Resources from Edutopia, ASCD, 'The First Days of School' (Harry Wong), ATD resources on facilitation",
            "instructional_design": "ADDIE model resources, Merrill's Principles of Instruction, Cathy Moore's blog (action mapping)",
            "educational_technology": "ISTE Standards, Google for Education resources, Common Sense Education, Articulate 360/Adobe Captivate tutorials (for e-learning development)"
        },
        "interview_focus": ["Teaching/training philosophy and methodology",
                            "Sample lesson plan presentation or training module delivery (demo)",
                            "Classroom/session management strategies",
                            "Experience with curriculum/course development and assessment/evaluation",
                            "Behavioral questions about handling challenging learners or situations",
                            "Knowledge of educational/training standards and current issues in the field"],
        "example_projects": [
            "Develop a unit plan for a specific grade level/subject or a training program for a corporate skill",
            "Create a portfolio of lesson plans/training materials and participant feedback/student work samples",
            "Design an innovative assessment method or evaluation strategy",
            "Present research on an educational topic or training methodology",
            "Volunteer or gain experience in classroom settings or delivering workshops"]
    }
}


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        name TEXT,
        current_role TEXT,
        desired_role_key TEXT,
        skills TEXT, -- JSON list of skills
        goals TEXT, -- JSON list of goals
        conversation_context TEXT, -- JSON blob for flexible state
        profile_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        sender TEXT NOT NULL, -- 'user' or 'ai'
        message_type TEXT DEFAULT 'text', -- 'text', 'quick_reply_prompt', 'resource_list'
        message_content TEXT NOT NULL, -- Can be Markdown or JSON for structured messages
        metadata TEXT, -- JSON for extra data (e.g., quick reply options)
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES users (session_id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")


app = FastAPI()


# --- AI Response Logic ---
def get_user_profile(session_id: str) -> dict:
    if session_id in USER_CONTEXT:
        return USER_CONTEXT[session_id]['data']

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, current_role, desired_role_key, skills, goals, conversation_context FROM users WHERE session_id = ?",
        (session_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        data = {
            'name': row[0],
            'current_role': row[1],
            'desired_role_key': row[2],
            'skills': json.loads(row[3]) if row[3] else [],
            'goals': json.loads(row[4]) if row[4] else [],
            'current_stage': 'general_query',
            'chat_topic': None
        }
        try:
            if row[5]:
                context_from_db = json.loads(row[5])
                data.update(context_from_db)
        except json.JSONDecodeError:
            logger.warning(f"Could not parse conversation_context for session {session_id}")

        USER_CONTEXT[session_id] = {'data': data, 'history_summary': ""}
        return data
    return {'name': None, 'current_role': None, 'desired_role_key': None, 'skills': [], 'goals': [],
            'current_stage': 'greeting', 'chat_topic': None}


def update_user_profile(session_id: str, data: dict):
    USER_CONTEXT.setdefault(session_id, {'data': {}, 'history_summary': ""})['data'].update(data)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET name=?, current_role=?, desired_role_key=?, skills=?, goals=?, conversation_context=?, last_active=CURRENT_TIMESTAMP
        WHERE session_id=?
    """, (
        data.get('name'),
        data.get('current_role'),
        data.get('desired_role_key'),
        json.dumps(data.get('skills', [])),
        json.dumps(data.get('goals', [])),
        json.dumps({k: v for k, v in data.items() if
                    k not in ['name', 'current_role', 'desired_role_key', 'skills', 'goals']}),
        session_id
    ))
    conn.commit()
    conn.close()


def generate_ai_response(session_id: str, user_message: str) -> dict:
    user_profile = get_user_profile(session_id)
    response_content = "I'm exploring how best to assist you. Could you clarify or try a different question? Type 'help' for options."
    response_type = "text"
    response_metadata = {}
    msg_lower = user_message.lower().strip()

    intent = "unknown"
    if user_profile['current_stage'] == 'greeting':
        intent = 'provide_name'
    elif user_profile['current_stage'] == 'get_name':
        intent = 'provide_name'
    elif user_profile['current_stage'] == 'get_current_role':
        intent = 'provide_current_role'
    elif user_profile['current_stage'] == 'get_desired_role':
        intent = 'provide_desired_role'
    elif user_profile['current_stage'] == 'get_skills':
        intent = 'provide_skills'
    elif any(k in msg_lower for k in ["help", "options", "what can you do"]):
        intent = 'get_help'
    elif any(k in msg_lower for k in ["reset", "start over"]):
        intent = 'reset_conversation'
    elif any(k in msg_lower for k in ["my name is", "call me"]) or (
            not user_profile.get('name') and len(msg_lower.split()) <= 3):
        intent = 'provide_name'
    elif any(k_word in msg_lower for path_data in CAREER_PATHS.values() for k_word in
             path_data['keywords'] + [path_data['name'].lower()]):
        intent = 'discuss_role'
    elif any(k in msg_lower for k in ["skill", "skills", "what should i learn", "gap analysis"]):
        intent = 'skill_analysis'
    elif any(k in msg_lower for k in ["resources", "learn", "courses", "books"]):
        intent = 'get_resources'
    elif any(k in msg_lower for k in ["interview", "preparation", "tips"]):
        intent = 'interview_prep'
    elif any(k in msg_lower for k in ["salary", "pay", "compensation"]):
        intent = 'salary_info'
    elif any(k in msg_lower for k in ["projects", "portfolio", "examples", "accomplishments"]):
        intent = 'project_ideas'
    elif any(k in msg_lower for k in ["thank", "thanks", "cool", "ok", "got it"]):
        intent = 'acknowledge'

    logger.info(
        f"Session {session_id}: Intent '{intent}', Stage '{user_profile['current_stage']}', Message '{user_message}'")

    if intent == 'reset_conversation':
        user_profile = {'name': None, 'current_role': None, 'desired_role_key': None, 'skills': [], 'goals': [],
                        'current_stage': 'greeting', 'chat_topic': None}
        response_content = "Okay, let's start fresh! I'm IntelliCoach, your AI Career Advisor. To begin, what's your name?"

    elif user_profile['current_stage'] == 'greeting':
        user_profile['current_stage'] = 'get_name'
        response_content = f"Hello! I'm IntelliCoach, your AI Career Advisor. It's wonderful to connect with you! To personalize our chat, what's your first name?"
        response_metadata = {'quick_replies': ["I prefer to stay anonymous for now."]}
        response_type = "quick_reply_prompt"

    elif intent == 'provide_name' or user_profile['current_stage'] == 'get_name':
        name_match = re.search(r"(?:my name is|call me|i am|i'm)\s*([a-zA-Z\s]+)", user_message, re.IGNORECASE)
        extracted_name = name_match.group(1).strip().title() if name_match else user_message.strip().title()
        if "anonymous" in extracted_name.lower() or len(extracted_name) > 25 or not extracted_name.replace(' ',
                                                                                                           '').isalpha():
            user_profile['name'] = "Explorer"
        else:
            user_profile['name'] = extracted_name

        response_content = f"Great to meet you, **{user_profile['name']}**! What is your current role or primary area of study?"
        user_profile['current_stage'] = 'get_current_role'
        update_user_profile(session_id, user_profile)

    elif intent == 'provide_current_role' or user_profile['current_stage'] == 'get_current_role':
        user_profile['current_role'] = user_message.strip()
        response_content = (
            f"Understood, {user_profile['current_role']}. Now, what career path are you most interested in exploring or pursuing? ")

        all_role_keys = list(CAREER_PATHS.keys())
        random.shuffle(all_role_keys)
        quick_reply_options = [CAREER_PATHS[k]['name'] for k in all_role_keys[:3]]
        if len(all_role_keys) > 3 and "Something else..." not in quick_reply_options:
            quick_reply_options.append("Something else...")

        response_content += f"For example: `{quick_reply_options[0]}`, `{quick_reply_options[1]}`"
        if len(quick_reply_options) > 2 and quick_reply_options[2] != "Something else...":
            response_content += f", or `{quick_reply_options[2]}`."
        else:
            response_content += "."

        user_profile['current_stage'] = 'get_desired_role'
        response_metadata = {'quick_replies': quick_reply_options}
        response_type = "quick_reply_prompt"
        update_user_profile(session_id, user_profile)

    elif intent == 'provide_desired_role' or intent == 'discuss_role' or user_profile[
        'current_stage'] == 'get_desired_role':
        matched_key = None
        for key, path_data in CAREER_PATHS.items():
            if msg_lower == path_data['name'].lower():
                matched_key = key
                break
        if not matched_key:
            for key, path_data in CAREER_PATHS.items():
                if any(keyword in msg_lower for keyword in path_data['keywords']):
                    matched_key = key
                    break
        if not matched_key:
            for key, path_data in CAREER_PATHS.items():
                if path_data['name'].lower() in msg_lower:
                    matched_key = key
                    break

        if matched_key:
            user_profile['desired_role_key'] = matched_key
            role_name = CAREER_PATHS[matched_key]['name']
            user_profile['chat_topic'] = 'role_overview'
            response_content = (f"Excellent choice, **{role_name}** is a dynamic field! Here's a quick overview:\n"
                                f"- **Summary**: {CAREER_PATHS[matched_key]['responsibilities_summary']}\n"
                                f"- **Key Skills**: {', '.join(CAREER_PATHS[matched_key]['required_skills'][:5])}...\n"
                                f"- **Salary Range (USD, approx.)**: {CAREER_PATHS[matched_key]['avg_salary_range']}\n\n"
                                f"Would you like to dive deeper into required skills, get a skill gap analysis (if you share your skills), or explore learning resources for this role?")
            user_profile['current_stage'] = 'general_query'
            response_metadata = {
                'quick_replies': ["Analyze my skills for this role", "Learning resources", "Interview tips",
                                  "Typical projects/accomplishments"]}
            response_type = "quick_reply_prompt"
        else:
            response_content = (
                "I'm not familiar with that specific role in my current database. Could you try phrasing it differently? "
                "You can also ask to 'explore roles' to see a list of careers I know about.")
        update_user_profile(session_id, user_profile)

    elif intent == 'skill_analysis' or user_profile['current_stage'] == 'get_skills':
        if not user_profile.get('desired_role_key'):
            response_content = "To perform a skill gap analysis, I first need to know your target career path. What role are you aiming for?"
            user_profile['current_stage'] = 'get_desired_role'
            all_role_keys = list(CAREER_PATHS.keys())
            random.shuffle(all_role_keys)
            response_metadata = {'quick_replies': [CAREER_PATHS[k]['name'] for k in all_role_keys[:3]]}
            response_type = "quick_reply_prompt"
        elif not user_profile.get('skills'):
            user_profile['current_stage'] = 'get_skills'
            response_content = "Sure, I can help with that! Please list your current technical and soft skills, separated by commas (e.g., Python, Project Management, Communication)."
        else:
            role_key = user_profile['desired_role_key']
            role_info = CAREER_PATHS[role_key]
            role_name = role_info['name']

            required_skills_normalized = set(
                skill.lower().strip().replace("_", " ") for skill in role_info['required_skills'])
            soft_skills_emphasis_normalized = set(
                skill.lower().strip().replace("_", " ") for skill in role_info.get('soft_skills_emphasis', []))
            all_target_skills = required_skills_normalized.union(soft_skills_emphasis_normalized)

            possessed_raw = user_profile.get('skills', [])
            possessed_normalized = set(skill.lower().strip().replace("_", " ") for skill in possessed_raw)

            missing_skills = sorted(list(all_target_skills - possessed_normalized))
            matching_skills = sorted(list(all_target_skills.intersection(possessed_normalized)))

            analysis_parts = [
                f"Okay, **{user_profile.get('name', 'Explorer')}**, here's a skill assessment for the **{role_name}** role based on your listed skills ({', '.join(possessed_raw)}):"]

            if matching_skills:
                analysis_parts.append(f"\n### Strengths (Skills you have that match):\n- " + "\n- ".join(
                    skill.title() for skill in matching_skills))
            else:
                analysis_parts.append(
                    f"\nIt seems we haven't listed skills that directly match the core requirements or emphasized soft skills for {role_name} yet. Let's identify them!")

            if missing_skills:
                analysis_parts.append(
                    f"\n### Areas for Development (Key skills to acquire/strengthen for {role_name}):\n- " + "\n- ".join(
                        skill.title() for skill in missing_skills))
                analysis_parts.append(f"\nI can suggest learning resources for these. What do you think?")
                response_metadata = {'quick_replies': [
                    f"Resources for {missing_skills[0].title()}" if missing_skills else "General resources",
                    "Tell me more about these skills", "Interview tips"]}
                response_type = "quick_reply_prompt"
            else:
                analysis_parts.append(
                    f"\nBased on your listed skills and the core requirements for {role_name}, you have a strong foundation! Consider exploring advanced topics or specializations within {role_name}.")
                response_metadata = {
                    'quick_replies': ["Project ideas/accomplishments", "Next career steps", "Interview tips"]}
                response_type = "quick_reply_prompt"

            response_content = "\n".join(analysis_parts)
            user_profile['current_stage'] = 'general_query'
            user_profile['chat_topic'] = 'skill_gap_results'
        update_user_profile(session_id, user_profile)

    elif intent == 'provide_skills':
        new_skills = [s.strip().lower() for s in user_message.split(',') if s.strip()]
        existing_skills = set(user_profile.get('skills', []))
        updated_skills = sorted(list(existing_skills.union(set(new_skills))))
        user_profile['skills'] = updated_skills
        update_user_profile(session_id, user_profile)

        if user_profile.get('desired_role_key'):
            return generate_ai_response(session_id, "skill gap analysis")
        else:
            response_content = f"Got it. Your skills: {', '.join(updated_skills)}. What's your target career path for a skill analysis?"
            user_profile['current_stage'] = 'get_desired_role'
            all_role_keys = list(CAREER_PATHS.keys())
            random.shuffle(all_role_keys)
            response_metadata = {'quick_replies': [CAREER_PATHS[k]['name'] for k in all_role_keys[:3]]}
            response_type = "quick_reply_prompt"

    elif intent == 'get_resources':
        if not user_profile.get('desired_role_key'):
            response_content = "To suggest the most relevant resources, I need to know your target role. What are you aiming for?"
            user_profile['current_stage'] = 'get_desired_role'
        else:
            role_key = user_profile['desired_role_key']
            role_info = CAREER_PATHS[role_key]
            role_name = role_info['name']
            resources = role_info['learning_resources']

            specific_skill_query = None
            for res_category_key in resources.keys():
                if res_category_key.replace("_", " ") in msg_lower or res_category_key in msg_lower:
                    specific_skill_query = res_category_key
                    break

            if specific_skill_query and specific_skill_query in resources:
                response_content = f"For **{specific_skill_query.replace('_', ' ').title()}** relevant to a **{role_name}**: {resources[specific_skill_query]}."
            else:
                resource_list = [f"### Learning Resources for **{role_name}**:\n"]
                if 'foundational' in resources:
                    resource_list.append(f"- **Foundational**: {resources['foundational']}")
                for category, resource_desc in list(resources.items()):
                    if category != 'foundational' and len(resource_list) < 6:
                        resource_list.append(f"- **{category.replace('_', ' ').title()}**: {resource_desc}")
                response_content = "\n".join(resource_list)
                response_content += "\n\nIs there a specific skill or area within this role you'd like to focus on?"
            user_profile['chat_topic'] = 'resources_provided'
            response_metadata = {
                'quick_replies': ["More on foundational skills", "Interview prep", f"Project ideas for {role_name}"]}
            response_type = "quick_reply_prompt"
        update_user_profile(session_id, user_profile)

    elif intent == 'interview_prep':
        if not user_profile.get('desired_role_key'):
            response_content = "To give you tailored interview tips, what role are you preparing for?"
            user_profile['current_stage'] = 'get_desired_role'
        else:
            role_key = user_profile['desired_role_key']
            role_info = CAREER_PATHS[role_key]
            role_name = role_info['name']

            tips = [
                "### General Interview Best Practices:",
                "- **Research**: Deeply understand the company, its products, and culture. Align your answers with their values.",
                "- **STAR Method**: For behavioral questions (Situation, Task, Action, Result). Prepare specific examples.",
                "- **Practice**: Conduct mock interviews. Record yourself to spot areas for improvement.",
                "- **Questions for Interviewer**: Prepare 2-3 insightful questions about the role, team, or company challenges.",
                "- **Logistics**: Test your tech for virtual interviews. For in-person, plan your route and arrive early.",
                "- **Follow-Up**: Send a personalized thank-you email within 24 hours.",
                f"\n### Specific Focus for **{role_name}** Interviews:",
                "- " + "\n- ".join(role_info['interview_focus']),
                "\nWould you like common behavioral questions, or example technical/role-specific questions for this role?"
            ]
            response_content = "\n".join(tips)
            user_profile['chat_topic'] = 'interview_tips_provided'
            response_metadata = {
                'quick_replies': ["Common behavioral questions", f"Role-specific questions for {role_name}",
                                  "Resources for this role"]}
            response_type = "quick_reply_prompt"
        update_user_profile(session_id, user_profile)

    elif intent == 'salary_info':
        if not user_profile.get('desired_role_key'):
            response_content = "To discuss salary, I need to know which role you're interested in."
            user_profile['current_stage'] = 'get_desired_role'
        else:
            role_key = user_profile['desired_role_key']
            role_info = CAREER_PATHS[role_key]
            response_content = f"The typical salary range for a **{role_info['name']}** in the US is approximately **{role_info['avg_salary_range']}**. This can vary significantly based on location, experience, company size, and specific skill set. Sites like Glassdoor, Levels.fyi, and LinkedIn Salary can provide more localized data."
        update_user_profile(session_id, user_profile)

    elif intent == 'project_ideas':
        if not user_profile.get('desired_role_key'):
            response_content = "For project ideas or example accomplishments, which career path are you targeting?"
            user_profile['current_stage'] = 'get_desired_role'
        else:
            role_key = user_profile['desired_role_key']
            role_info = CAREER_PATHS[role_key]
            project_type_term = "projects"
            if "manager" in role_key or "hr" in role_key or "teacher" in role_key or "educator" in role_key:
                project_type_term = "accomplishments or key responsibilities"
            elif "designer" in role_key:
                project_type_term = "portfolio items"

            if 'example_projects' in role_info and role_info['example_projects']:
                response_content = f"### Example {project_type_term.capitalize()} for a **{role_info['name']}**:\n- " + "\n- ".join(
                    role_info['example_projects'])
                response_content += f"\n\nBuilding relevant {project_type_term} is a great way to learn and showcase your skills!"
            else:
                response_content = f"I don't have specific {project_type_term} for {role_info['name']} right now, but generally, look for experiences that allow you to practice the core skills of the role and solve a real (even small) problem or demonstrate key competencies."
        update_user_profile(session_id, user_profile)

    elif intent == 'get_help':
        name_clause = f"{user_profile['name']}, " if user_profile.get('name') and user_profile[
            'name'] != "Explorer" else ""
        options = [
            "Explore career paths (e.g., 'Tell me about Software Engineering')",
            "Get a skill gap analysis (e.g., 'Analyze my skills for Data Science')",
            "Find learning resources (e.g., 'Resources for Python')",
            "Receive interview tips (e.g., 'Interview prep for Product Manager')",
            "Discuss salary expectations",
            "Get project ideas for a role",
            "Update my skills (e.g., 'I know JavaScript')",
            "Type 'reset' to start our conversation over."
        ]
        response_content = f"Hi {name_clause}I can help you with:\n- " + "\n- ".join(options)
        response_metadata = {'quick_replies': ["Explore career paths", "Skill gap analysis", "Learning resources"]}
        response_type = "quick_reply_prompt"

    elif intent == 'acknowledge':
        response_content = "Great! What would you like to explore next?"
        response_metadata = {'quick_replies': ["Skill gap analysis", "Learning resources", "Interview tips", "Help"]}
        response_type = "quick_reply_prompt"
        if user_profile.get('desired_role_key'):
            response_metadata['quick_replies'].insert(0,
                                                      f"More about {CAREER_PATHS[user_profile['desired_role_key']]['name']}")

    elif user_profile['current_stage'] == 'general_query' and intent == 'unknown':
        name_clause = f"{user_profile.get('name', 'Explorer')}, " if user_profile.get('name') and user_profile[
            'name'] != "Explorer" else ""
        response_content = f"Hmm, I'm not sure how to respond to that, {name_clause}. You can ask me about career paths, skills, resources, or interview prep. Try 'help' for more options!"
        response_metadata = {'quick_replies': ["Help", "Explore career paths", "Skill gap analysis"]}
        response_type = "quick_reply_prompt"

    final_response = {
        "reply": response_content,
        "type": response_type,
        "metadata": response_metadata
    }
    return final_response


# --- HTML, CSS, JS Content ---
def generate_html_content(session_id=None, itemsContent=None):
    user_name = "Explorer"
    initial_ai_message_obj = {
        "reply": "Hello! I'm IntelliCoach, your AI Career Advisor. It's wonderful to connect with you! To personalize our chat, what's your first name?",
        "type": "quick_reply_prompt", "metadata": {"quick_replies": ["I prefer to stay anonymous for now."]}}

    chat_history_html = ""
    if session_id:
        profile = get_user_profile(session_id)
        if profile.get('name'): user_name = profile['name']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT sender, message_content, message_type, metadata FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC LIMIT 100",
            (session_id,))
        history = cursor.fetchall()
        conn.close()

        if not history:
            chat_history_html += f'<div class="message ai-message" data-type="{initial_ai_message_obj["type"]}" data-metadata=\'{json.dumps(initial_ai_message_obj["metadata"])}\'><div>{render_markdown(initial_ai_message_obj["reply"])}</div></div>'
        else:
            for sender, message_content, message_type, metadata_json in history:
                message_class = "user-message" if sender == "user" else "ai-message"
                processed_message = escape_html(message_content) if sender == "user" else render_markdown(
                    message_content)

                metadata_attr = ""
                if metadata_json:
                    try:
                        parsed_meta = json.loads(metadata_json)
                        metadata_attr = f"data-metadata='{escape_html(json.dumps(parsed_meta))}'"
                    except json.JSONDecodeError:
                        logger.error(f"Invalid metadata JSON in history: {metadata_json}")

                chat_history_html += f'<div class="message {message_class}" data-type="{message_type}" {metadata_attr}><div>{processed_message}</div></div>'
    else:
        chat_history_html += f'<div class="message ai-message" data-type="{initial_ai_message_obj["type"]}" data-metadata=\'{json.dumps(initial_ai_message_obj["metadata"])}\'><div>{render_markdown(initial_ai_message_obj["reply"])}</div></div>'

    send_icon_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z"/></svg>'
    user_avatar_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="user-avatar-icon"><path fill-rule="evenodd" d="M18.685 19.097A9.723 9.723 0 0021.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 003.065 7.097A9.716 9.716 0 0012 21.75a9.716 9.716 0 006.685-2.653zm-12.54-1.285A7.486 7.486 0 0112 15a7.486 7.486 0 015.855 2.812A8.224 8.224 0 0112 20.25a8.224 8.224 0 01-5.855-2.438zM15.75 9a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" clip-rule="evenodd" /></svg>'

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IntelliCoach Pro - Your AI Career Partner</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Lexend:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-accent: #007AFF; 
            --secondary-accent: #34C759; 
            --background-main: #f8f9fa; 
            --background-chat: #ffffff;
            --text-primary: #1c1c1e;
            --text-secondary: #636366;
            --text-on-accent: #ffffff;
            --border-light: #e5e5ea;
            --user-msg-bg: var(--primary-accent);
            --user-msg-text: var(--text-on-accent);
            --ai-msg-bg: #e9ecef; 
            --ai-msg-text: var(--text-primary);
            --header-bg: linear-gradient(135deg, #007AFF, #0056b3);
            --font-main: 'Inter', sans-serif;
            --font-headings: 'Lexend', sans-serif;
            --border-radius-main: 12px;
            --border-radius-msg: 18px;
            --shadow-light: 0 2px 8px rgba(0,0,0,0.06);
            --shadow-medium: 0 6px 16px rgba(0,0,0,0.1);
        }}
        *, *::before, *::after {{ box-sizing: border-box; }}
        body {{
            font-family: var(--font-main);
            margin: 0;
            background-color: var(--background-main);
            color: var(--text-primary);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 1rem;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        .chat-app-container {{
            width: 100%;
            max-width: 800px;
            height: clamp(500px, 90vh, 900px);
            background-color: var(--background-chat);
            border-radius: var(--border-radius-main);
            box-shadow: var(--shadow-medium);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .chat-header {{
            background: var(--header-bg);
            color: var(--text-on-accent);
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid transparent; 
            z-index: 10;
        }}
        .chat-header-title {{
            font-family: var(--font-headings);
            font-size: 1.5rem;
            font-weight: 600;
        }}
        .chat-header-user-info {{
            display: flex;
            align-items: center;
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        .user-avatar-icon {{ width: 24px; height: 24px; margin-right: 0.5rem; }}

        .chat-messages-area {{
            flex-grow: 1;
            padding: 1.5rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            background-color: var(--background-main); 
        }}
        .message {{
            display: flex;
            max-width: 85%;
            opacity: 0;
            transform: translateY(10px);
            animation: messageFadeIn 0.3s ease-out forwards;
        }}
        .message div {{ 
            padding: 0.75rem 1.25rem;
            border-radius: var(--border-radius-msg);
            line-height: 1.6;
            word-wrap: break-word;
            font-size: 0.95rem;
            box-shadow: var(--shadow-light);
        }}
        .user-message {{ align-self: flex-end; margin-left: auto; }}
        .user-message div {{
            background-color: var(--user-msg-bg);
            color: var(--user-msg-text);
            border-bottom-right-radius: 4px;
        }}
        .ai-message {{ align-self: flex-start; }}
        .ai-message div {{
            background-color: var(--ai-msg-bg);
            color: var(--ai-msg-text);
            border-bottom-left-radius: 4px;
        }}
        .ai-message strong {{ color: var(--primary-accent); font-weight: 600; }}
        .ai-message em {{ font-style: italic; }}
        .ai-message ul, .ai-message ol {{ margin-top: 0.5em; margin-bottom: 0.5em; padding-left: 1.5em; }}
        .ai-message li {{ margin-bottom: 0.25em; }}
        .ai-message h3 {{ font-family: var(--font-headings); font-size: 1.1em; margin-top:0.8em; margin-bottom:0.4em; color: var(--primary-accent); }}
        .ai-message a {{ color: var(--primary-accent); text-decoration: none; font-weight: 500; }}
        .ai-message a:hover {{ text-decoration: underline; }}
        .ai-message code {{ background-color: #d1d5db; padding: 0.2em 0.4em; border-radius: 4px; font-family: monospace; font-size: 0.9em; }}

        .quick-replies-container {{
            padding: 0.5rem 0 0; 
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: flex-start; 
            margin-top: 0.5rem; 
            margin-left: 0; 
        }}
        .quick-reply-button {{
            background-color: #fff;
            color: var(--primary-accent);
            border: 1px solid var(--primary-accent);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        .quick-reply-button:hover {{
            background-color: var(--primary-accent);
            color: #fff;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,122,255,0.2);
        }}

        .chat-input-area {{
            display: flex;
            padding: 1rem 1.5rem;
            border-top: 1px solid var(--border-light);
            background-color: var(--background-chat); 
        }}
        .chat-input-area input[type="text"] {{
            flex-grow: 1;
            padding: 0.85rem 1.25rem;
            border: 1px solid var(--border-light);
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .chat-input-area input[type="text"]:focus {{
            border-color: var(--primary-accent);
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
        }}
        .chat-input-area button#sendButton {{
            background: var(--primary-accent);
            color: var(--text-on-accent);
            border: none;
            width: 48px; 
            height: 48px;
            margin-left: 0.75rem;
            border-radius: 50%; 
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s, transform 0.1s;
        }}
        .chat-input-area button#sendButton:hover {{ background-color: #0056b3; }}
        .chat-input-area button#sendButton:active {{ transform: scale(0.95); }}
        .chat-input-area button#sendButton:disabled {{ background-color: #cdd2d8; cursor: not-allowed; }}
        .chat-input-area button#sendButton svg {{ width: 22px; height: 22px; }}

        .typing-indicator {{ 
        }}
        .typing-indicator div {{ 
            padding: 0.8rem 1.1rem; 
            display: flex;
            align-items: center;
        }}
        .typing-indicator span {{
            display: inline-block;
            width: 8px; height: 8px; margin: 0 3px; 
            background-color: #adb5bd;
            border-radius: 50%;
            animation: typingAnimation 1.4s infinite both; 
        }}
        .typing-indicator span:nth-child(1) {{ animation-delay: 0s; }}
        .typing-indicator span:nth-child(2) {{ animation-delay: 0.2s; }}
        .typing-indicator span:nth-child(3) {{ animation-delay: 0.4s; }}

        @keyframes messageFadeIn {{
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes typingAnimation {{ 
            0%, 80%, 100% {{ transform: scale(0); opacity: 0.5; }}
            40% {{ transform: scale(1.0); opacity: 1; }}
        }}
        .chat-messages-area::-webkit-scrollbar {{ width: 8px; }}
        .chat-messages-area::-webkit-scrollbar-track {{ background: transparent; }}
        .chat-messages-area::-webkit-scrollbar-thumb {{ background: #ced4da; border-radius: 4px; }}
        .chat-messages-area::-webkit-scrollbar-thumb:hover {{ background: #adb5bd; }}

        @media (max-width: 768px) {{
            body {{ padding: 0; }}
            .chat-app-container {{ height: 100vh; max-height: none; border-radius: 0; }}
            .chat-header-title {{ font-size: 1.25rem; }}
            .chat-messages-area, .chat-input-area, .chat-header {{ padding-left: 1rem; padding-right: 1rem; }}
            .message div {{ font-size: 0.9rem; }}
        }}
    </style>
</head>
<body>
    <div class="chat-app-container">
        <div class="chat-header">
            <div class="chat-header-title">IntelliCoach Pro</div>
            <div class="chat-header-user-info">
                {user_avatar_svg}
                <span id="userNameDisplay">{user_name}</span>
            </div>
        </div>
        <div class="chat-messages-area" id="chatMessagesArea">
            {chat_history_html}
        </div>
        <div class="chat-input-area">
            <input type="text" id="userInput" placeholder="Ask about careers, skills, or interviews..." autocomplete="off">
            <button id="sendButton" aria-label="Send Message">
                {send_icon_svg}
            </button>
        </div>
    </div>

    <script>
        const chatMessagesArea = document.getElementById('chatMessagesArea');
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');
        const userNameDisplay = document.getElementById('userNameDisplay');
        let typingIndicatorElement = null;

        function escapeHtml(unsafe) {{
            if (typeof unsafe !== 'string') return unsafe;
            return unsafe
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }}

        function renderClientMarkdown(md) {{
            if (typeof md !== 'string') return md;
            let html = escapeHtml(md); 
            // Bold
            html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
                       .replace(/__([^_]+)__/g, '<strong>$1</strong>');
            // Italics - carefully to avoid parts of bold
            html = html.replace(/(?<![a-zA-Z0-9*])\\*(?!\\s|\\*)([^\\*\\n]+?)(?<!\\s|\\*)\\*(?![a-zA-Z0-9*])/g, '<em>$1</em>')
                       .replace(/(?<![a-zA-Z0-9_])_(?!\\s|_)([^_\\n]+?)(?<!\\s|_)_(?![a-zA-Z0-9_])/g, '<em>$1</em>');

            // Headers
            html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');

            // Lists
            html = html.replace(/^[-*+]\s+(.*$)/gim, '<li>$1</li>');

            // Function to wrap list items; Python's f-string requires {{ and }} for literal braces.
            // For JavaScript template literals `${{var}}`, the dollar sign is literal, and {{var}} produces {var}.
            function clientWrapListItems(match) {{
                let itemsContent = match.replace(/<\\/li>\\s*(<br\\s*\\/?>\\s*)+\\s*<li>/gi, '</li><li>'); // Use escaped slash for Python f-string
                itemsContent = itemsContent.replace(/^\\s*(<br\\s*\\/?>\\s*)+|(<br\\s*\\/?>\\s*)+\\s*$/g, '');
                return `<ul>${{itemsContent}}</ul>`; // Corrected for Python f-string: ${{itemsContent}} -> ${itemsContent} in JS
            }}
            html = html.replace(/(?:<li>.*?<\\/li>\\s*(?:<br\\s*\\/?>\\s*)*)+/gs, clientWrapListItems); // Use escaped slash

            // Links
            html = html.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'); // Escaped \ and ( )
            // Code
            html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
            // Newlines
            html = html.replace(/\\n/g, '<br>'); // Escaped \

            // Cleanup <br> tags
            html = html.replace(/<ul>(<br\\s*\\/?>\\s*)+/g, '<ul>');
            html = html.replace(/(<br\\s*\\/?>\\s*)+<\\/ul>/g, '</ul>'); // Escaped /
            html = html.replace(/<li>(<br\\s*\\/?>\\s*)+/g, '<li>');
            html = html.replace(/(<br\\s*\/?>\\s*)+<\\/li>/g, '</li>'); // Escaped /
            return html;
        }}

        function showTypingIndicator() {{
            if (!typingIndicatorElement) {{
                typingIndicatorElement = document.createElement('div');
                typingIndicatorElement.classList.add('message', 'ai-message', 'typing-indicator'); 
                typingIndicatorElement.innerHTML = `<div><span></span><span></span><span></span></div>`;
                chatMessagesArea.appendChild(typingIndicatorElement);
            }}
            typingIndicatorElement.style.display = 'flex'; 
            scrollToBottom();
        }}

        function hideTypingIndicator() {{
            if (typingIndicatorElement) {{
                typingIndicatorElement.style.display = 'none';
            }}
        }}

        function removeAllQuickReplies() {{
             document.querySelectorAll('.quick-replies-container').forEach(el => el.remove());
        }}

        function addMessageToChat(content, sender, type = 'text', metadata = null) {{
            if (sender === 'user' || (sender === 'ai' && (!metadata || !metadata.quick_replies))) {{
                 removeAllQuickReplies(); 
            }}

            const messageWrapper = document.createElement('div');
            messageWrapper.classList.add('message', sender + '-message');
            messageWrapper.dataset.type = type;
            if (metadata && typeof metadata === 'object') {{
                 messageWrapper.dataset.metadata = JSON.stringify(metadata);
            }}

            const messageContentElement = document.createElement('div');
            messageContentElement.innerHTML = (sender === 'user') ? escapeHtml(content) : renderClientMarkdown(content);

            messageWrapper.appendChild(messageContentElement);
            chatMessagesArea.appendChild(messageWrapper);

            if (sender === 'ai' && type === 'quick_reply_prompt' && metadata && metadata.quick_replies && metadata.quick_replies.length > 0) {{
                const quickRepliesContainer = document.createElement('div');
                quickRepliesContainer.classList.add('quick-replies-container');
                metadata.quick_replies.forEach(replyText => {{
                    const button = document.createElement('button');
                    button.classList.add('quick-reply-button');
                    button.textContent = replyText;
                    button.onclick = () => handleQuickReply(replyText);
                    quickRepliesContainer.appendChild(button);
                }});
                chatMessagesArea.appendChild(quickRepliesContainer); 
            }}
            scrollToBottom();
        }}

        function scrollToBottom() {{
            requestAnimationFrame(() => {{
                 chatMessagesArea.scrollTop = chatMessagesArea.scrollHeight;
            }});
        }}

        function handleQuickReply(replyText) {{
            addMessageToChat(replyText, 'user'); 
            userInput.value = ''; 
            userInput.disabled = true;
            sendButton.disabled = true;
            showTypingIndicator();

            removeAllQuickReplies();

            fetch('/chat', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                body: new URLSearchParams({{ 'message': replyText }})
            }})
            .then(response => {{
                if (!response.ok) throw new Error(`HTTP error! Status: ${{response.status}}`);
                return response.json();
            }})
            .then(data => {{
                addMessageToChat(data.reply, 'ai', data.type, data.metadata);
                if (data.profile_update && data.profile_update.name) {{
                    userNameDisplay.textContent = data.profile_update.name;
                }}
            }})
            .catch(error => {{
                console.error('Error sending quick reply:', error);
                addMessageToChat('Sorry, I encountered an issue. Please try again.', 'ai');
            }})
            .finally(() => {{
                hideTypingIndicator();
                userInput.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
            }});
        }}

        async function handleSendMessage() {{
            const messageText = userInput.value.trim();
            if (messageText === '') return;

            addMessageToChat(messageText, 'user');
            userInput.value = '';
            userInput.disabled = true;
            sendButton.disabled = true;
            showTypingIndicator();

            removeAllQuickReplies();

            try {{
                const response = await fetch('/chat', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                    body: new URLSearchParams({{ 'message': messageText }})
                }});

                if (!response.ok) {{
                    const errorData = await response.json().catch(() => ({{detail: "An unknown error occurred."}}));
                    addMessageToChat(`Error: ${{response.status}} - ${{errorData.detail || "Could not reach advisor."}}`, 'ai');
                    return;
                }}

                const data = await response.json();
                addMessageToChat(data.reply, 'ai', data.type, data.metadata);
                 if (data.profile_update && data.profile_update.name) {{
                    userNameDisplay.textContent = data.profile_update.name;
                }}

            }} catch (error) {{
                console.error('Error sending message:', error);
                addMessageToChat('Oops! I seem to be having trouble connecting. Please check your connection or try again.', 'ai');
            }} finally {{
                hideTypingIndicator();
                userInput.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
            }}
        }}

        sendButton.addEventListener('click', handleSendMessage);
        userInput.addEventListener('keypress', (event) => {{
            if (event.key === 'Enter' && !event.shiftKey) {{
                event.preventDefault();
                handleSendMessage();
            }}
        }});

        function processInitialMessagesForQuickReplies() {{
            const aiMessages = Array.from(chatMessagesArea.querySelectorAll('.message.ai-message'));
            const lastAIMessage = aiMessages.pop(); 

            if (lastAIMessage) {{
                const type = lastAIMessage.dataset.type;
                const metadataString = lastAIMessage.dataset.metadata;

                if (type === 'quick_reply_prompt' && metadataString) {{
                    try {{
                        const metadata = JSON.parse(metadataString);
                        if (metadata && metadata.quick_replies && metadata.quick_replies.length > 0) {{
                            let nextSibling = lastAIMessage.nextElementSibling;
                            if (!nextSibling || !nextSibling.classList.contains('quick-replies-container')) {{
                                const quickRepliesContainer = document.createElement('div');
                                quickRepliesContainer.classList.add('quick-replies-container');
                                metadata.quick_replies.forEach(replyText => {{
                                    const button = document.createElement('button');
                                    button.classList.add('quick-reply-button');
                                    button.textContent = replyText;
                                    button.onclick = () => handleQuickReply(replyText);
                                    quickRepliesContainer.appendChild(button);
                                }});
                                lastAIMessage.parentNode.insertBefore(quickRepliesContainer, lastAIMessage.nextSibling);
                            }}
                        }}
                    }} catch (e) {{
                        console.error("Error parsing metadata for quick replies on load:", e, metadataString);
                    }}
                }}
            }}
        }}

        window.onload = () => {{
            processInitialMessagesForQuickReplies(); 
            scrollToBottom();
            userInput.focus();
        }};
    </script>
</body>
</html>
    """
    return html_template


def render_markdown(text: str) -> str:
    if not isinstance(text, str): return str(text)

    html = escape_html(text)

    html = re.sub(r'^### (.*)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)

    html = re.sub(r'(?<![a-zA-Z0-9*])\*(?!\s|\*)([^\*\n]+?)(?<!\s|\*)\*(?![a-zA-Z0-9*])', r'<em>\1</em>', html)
    html = re.sub(r'(?<![a-zA-Z0-9_])_(?!\s|_)([^_\n]+?)(?<!\s|_)_(?![a-zA-Z0-9_])', r'<em>\1</em>', html)

    html = re.sub(r'^\s*[-*+]\s+(.*)', r'<li>\1</li>', html, flags=re.MULTILINE)

    def wrap_list_items_server(match_obj):
        list_items_content = match_obj.group(0)
        cleaned_content = re.sub(r'</li>\s*(?:<br\s*\/?>\s*)+\s*<li>', '</li><li>', list_items_content)
        cleaned_content = re.sub(r'^\s*(<br\s*\/?>\s*)+', '', cleaned_content)
        cleaned_content = re.sub(r'(<br\s*\/?>\s*)+\s*$', '', cleaned_content)
        return f"<ul>{cleaned_content}</ul>"

    html = re.sub(r'(?:<li>.*?</li>\s*(?:<br\s*\/?>\s*)*)+', wrap_list_items_server, html, flags=re.DOTALL)

    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    html = html.replace("\n", "<br>")

    html = re.sub(r'<ul><br\s*\/?>', '<ul>', html)
    html = re.sub(r'<br\s*\/?></ul>', '</ul>', html)
    html = re.sub(r'<li><br\s*\/?>', '<li>', html)
    html = re.sub(r'<br\s*\/?></li>', '</li>', html)

    return html


def escape_html(unsafe_text: str) -> str:
    if not isinstance(unsafe_text, str): return str(unsafe_text)
    return unsafe_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace(
        "'", "&#039;")


# --- FastAPI Endpoints ---
@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    session_id = request.cookies.get("session_id")
    response_html_content = ""

    if not session_id or not UserSessionManager.session_exists_in_db(session_id):
        session_id = secrets.token_hex(24)
        UserSessionManager.create_user_session_db(session_id)
        USER_CONTEXT[session_id] = {
            'data': {'name': None, 'current_role': None, 'desired_role_key': None, 'skills': [], 'goals': [],
                     'current_stage': 'greeting', 'chat_topic': None}, 'history_summary': ""}

        response_html_content = generate_html_content(session_id)
        response = HTMLResponse(content=response_html_content)
        response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="Lax",
                            max_age=30 * 24 * 60 * 60, secure=False)
        return response

    if session_id not in USER_CONTEXT:
        profile_data = get_user_profile(session_id)
        if not profile_data or profile_data.get('current_stage') is None:
            USER_CONTEXT[session_id] = {
                'data': {'name': None, 'current_role': None, 'desired_role_key': None, 'skills': [], 'goals': [],
                         'current_stage': 'greeting', 'chat_topic': None}, 'history_summary': ""}
            logger.warning(f"Re-initialized empty context for existing session_id {session_id}")

    response_html_content = generate_html_content(session_id)
    return HTMLResponse(content=response_html_content)


@app.post("/chat")
async def chat_endpoint(request: Request, message: str = Form(...)):
    session_id = request.cookies.get("session_id")
    if not session_id or not UserSessionManager.session_exists_in_db(session_id):
        logger.warning(f"Chat attempt with invalid/missing session_id. Message: {message}")
        raise HTTPException(status_code=400, detail="Invalid or expired session. Please refresh the page.")

    if session_id not in USER_CONTEXT:
        get_user_profile(session_id)
        if session_id not in USER_CONTEXT:
            logger.error(f"CRITICAL: USER_CONTEXT not populated for session {session_id} after get_user_profile call.")
            USER_CONTEXT[session_id] = {
                'data': {'name': None, 'current_role': None, 'desired_role_key': None, 'skills': [], 'goals': [],
                         'current_stage': 'greeting', 'chat_topic': None}, 'history_summary': ""}

    user_message_clean = message.strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (session_id, sender, message_type, message_content, metadata) VALUES (?, ?, ?, ?, ?)",
        (session_id, 'user', 'text', user_message_clean, None))
    conn.commit()

    ai_response_obj = generate_ai_response(session_id, user_message_clean)

    cursor.execute(
        "INSERT INTO chat_history (session_id, sender, message_type, message_content, metadata) VALUES (?, ?, ?, ?, ?)",
        (session_id, 'ai', ai_response_obj['type'], ai_response_obj['reply'], json.dumps(ai_response_obj['metadata'])))
    conn.commit()
    conn.close()

    profile_update_info = {}
    current_profile = get_user_profile(session_id)
    if current_profile.get('name'):
        profile_update_info['name'] = current_profile['name']

    return JSONResponse({
        "reply": ai_response_obj['reply'],
        "type": ai_response_obj['type'],
        "metadata": ai_response_obj['metadata'],
        "profile_update": profile_update_info
    })


# --- DB Helper Class for User Session Management ---
class UserSessionManager:
    @staticmethod
    def create_user_session_db(session_id: str):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (session_id, skills, goals, conversation_context) VALUES (?, ?, ?, ?)",
                           (session_id, json.dumps([]), json.dumps([]), json.dumps({'current_stage': 'greeting'})))
            conn.commit()
            logger.info(f"Created new user session in DB: {session_id}")
        except sqlite3.IntegrityError:
            logger.warning(f"Session {session_id} already exists in DB, insert failed.")
        finally:
            conn.close()

    @staticmethod
    def session_exists_in_db(session_id: str) -> bool:
        if not session_id: return False
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE session_id = ?", (session_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists


# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Initializing IntelliCoach Pro...")
    init_db()
    module_name = __file__.replace(".py", "").split("/")[-1].split("\\")[-1]
    logger.info(f"Starting IntelliCoach Pro server on http://127.0.0.1:8000 "
                f"(running '{module_name}:app' with uvicorn)")
    uvicorn.run(f"{module_name}:app", host="127.0.0.1", port=8000, reload=True)
