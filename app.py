# ============================================================
# AI RESUME MAKER - COMPLETE APP
# Login + Signup + Create + Edit + Update + Delete + PDF
# ============================================================

import streamlit as st
import sqlite3
import hashlib
import os
import html
from datetime import datetime
from dotenv import load_dotenv

from resume_generator import generate_resume
from pdf_renderer import text_to_pdf


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume Maker",
    page_icon="📄",
    layout="wide"
)

load_dotenv()


# ============================================================
# DATABASE
# ============================================================

DB_NAME = "resume_database.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT,
            job_title TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            linkedin TEXT,
            portfolio TEXT,
            summary TEXT,
            skills TEXT,
            education TEXT,
            certifications TEXT,
            experience TEXT,
            languages TEXT,
            interests TEXT,
            achievements TEXT,
            style TEXT,
            template TEXT,
            resume_text TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


create_tables()


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name, email, password):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(email, password):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, hash_password(password))
    )

    user = cursor.fetchone()
    conn.close()

    return user


# ============================================================
# RESUME DATABASE FUNCTIONS
# ============================================================

def save_resume(user_id, data, resume_text):
    conn = get_db()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO resumes (
            user_id,
            name,
            job_title,
            email,
            phone,
            location,
            linkedin,
            portfolio,
            summary,
            skills,
            education,
            certifications,
            experience,
            languages,
            interests,
            achievements,
            style,
            template,
            resume_text,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data["name"],
        data["job_title"],
        data["email"],
        data["phone"],
        data["location"],
        data["linkedin"],
        data["portfolio"],
        data["summary"],
        data["skills"],
        data["education"],
        data["certifications"],
        data["experience"],
        data["languages"],
        data["interests"],
        data["achievements"],
        data["style"],
        data["template"],
        resume_text,
        now,
        now
    ))

    resume_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return resume_id


def get_user_resumes(user_id):
    conn = get_db()

    resumes = conn.execute("""
        SELECT *
        FROM resumes
        WHERE user_id = ?
        ORDER BY updated_at DESC
    """, (user_id,)).fetchall()

    conn.close()

    return resumes


def get_resume(resume_id, user_id):
    conn = get_db()

    resume = conn.execute("""
        SELECT *
        FROM resumes
        WHERE id = ? AND user_id = ?
    """, (resume_id, user_id)).fetchone()

    conn.close()

    return resume


def update_resume(resume_id, user_id, data, resume_text):
    conn = get_db()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("""
        UPDATE resumes
        SET
            name = ?,
            job_title = ?,
            email = ?,
            phone = ?,
            location = ?,
            linkedin = ?,
            portfolio = ?,
            summary = ?,
            skills = ?,
            education = ?,
            certifications = ?,
            experience = ?,
            languages = ?,
            interests = ?,
            achievements = ?,
            style = ?,
            template = ?,
            resume_text = ?,
            updated_at = ?
        WHERE id = ? AND user_id = ?
    """, (
        data["name"],
        data["job_title"],
        data["email"],
        data["phone"],
        data["location"],
        data["linkedin"],
        data["portfolio"],
        data["summary"],
        data["skills"],
        data["education"],
        data["certifications"],
        data["experience"],
        data["languages"],
        data["interests"],
        data["achievements"],
        data["style"],
        data["template"],
        resume_text,
        now,
        resume_id,
        user_id
    ))

    conn.commit()
    conn.close()


def delete_resume(resume_id, user_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM resumes WHERE id = ? AND user_id = ?",
        (resume_id, user_id)
    )

    conn.commit()
    conn.close()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "page" not in st.session_state:
    st.session_state.page = "create"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = None


# ============================================================
# RESUME PREVIEW FUNCTION
# ============================================================

def format_resume_for_display(text):

    lines = text.split("\n")
    html_lines = []

    in_list = False

    section_keywords = [
        "PROFESSIONAL SUMMARY",
        "SUMMARY",
        "SKILLS",
        "TECHNICAL SKILLS",
        "EDUCATION",
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "PROJECTS",
        "CERTIFICATIONS",
        "ACHIEVEMENTS",
        "OBJECTIVE",
        "LANGUAGES",
        "INTERESTS"
    ]

    for line in lines:

        line = line.strip()

        if not line:

            if in_list:
                html_lines.append("</ul>")
                in_list = False

            continue

        safe_line = html.escape(line)

        # Name
        if (
            not html_lines
            and not line.startswith(("•", "-", "*"))
        ):
            html_lines.append(
                f'<h1>{safe_line}</h1>'
            )
            continue

        # Section
        upper_line = line.upper()

        if (
            upper_line.rstrip(":") in section_keywords
            or any(
                upper_line.startswith(keyword + ":")
                for keyword in section_keywords
            )
        ):

            if in_list:
                html_lines.append("</ul>")
                in_list = False

            section_name = safe_line.rstrip(":")

            html_lines.append(
                f"<h2>{section_name}</h2>"
            )

            continue

        # Bullet
        if line.startswith(("•", "-", "*")):

            bullet_text = html.escape(
                line[1:].strip()
            )

            if not in_list:
                html_lines.append("<ul>")
                in_list = True

            html_lines.append(
                f"<li>{bullet_text}</li>"
            )

        else:

            if in_list:
                html_lines.append("</ul>")
                in_list = False

            html_lines.append(
                f"<p>{safe_line}</p>"
            )

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


# ============================================================
# LOGIN / SIGNUP PAGE
# ============================================================

def authentication_page():

    st.markdown(
        """
        <style>
        .main-title {
            text-align: center;
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .sub-title {
            text-align: center;
            color: gray;
            font-size: 18px;
            margin-bottom: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-title">📄 AI Resume Maker</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Create professional resumes with AI</div>',
        unsafe_allow_html=True
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    with login_tab:

        st.subheader("Welcome Back!")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Please enter email and password."
                )

            else:

                user = login_user(
                    email,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.user_name = user["name"]
                    st.session_state.page = "create"

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

    # --------------------------------------------------------
    # SIGNUP
    # --------------------------------------------------------

    with signup_tab:

        st.subheader("Create Your Account")

        name = st.text_input(
            "Full Name",
            key="signup_name"
        )

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "📝 Create Account",
            use_container_width=True
        ):

            if not name or not email or not password:

                st.error(
                    "Please fill all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success = register_user(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(
                        "Account created successfully! Please login."
                    )

                else:

                    st.error(
                        "This email is already registered."
                    )


# ============================================================
# STOP HERE IF NOT LOGGED IN
# ============================================================

if not st.session_state.logged_in:

    authentication_page()
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📄 AI Resume Maker")

    st.write(
        f"Welcome, **{st.session_state.user_name}**"
    )

    st.markdown("---")

    if st.button(
        "➕ Create New Resume",
        use_container_width=True
    ):

        st.session_state.page = "create"
        st.session_state.edit_id = None
        st.session_state.generated_resume = None

        st.rerun()

    if st.button(
        "📂 My Resumes",
        use_container_width=True
    ):

        st.session_state.page = "my_resumes"
        st.session_state.generated_resume = None

        st.rerun()

    st.markdown("---")

    st.subheader("⚙️ AI Settings")

    use_ai = st.checkbox(
        "Use AI Generation",
        value=True
    )

    if use_ai:

        default_key = os.getenv(
            "GEMINI_API_KEY",
            ""
        )

        if default_key:

            st.success("✅ API Key loaded")

            api_key = default_key

        else:

            st.info(
                "Enter your Gemini API key below."
            )

            api_key = st.text_input(
                "Google Gemini API Key",
                type="password"
            )

    else:

        api_key = None

    st.markdown("---")

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.page = "create"
        st.session_state.edit_id = None

        st.rerun()


# ============================================================
# MY RESUMES PAGE
# ============================================================

if st.session_state.page == "my_resumes":

    st.title("📂 My Resumes")

    resumes = get_user_resumes(
        st.session_state.user_id
    )

    if not resumes:

        st.info(
            "You have not created any resumes yet."
        )

        if st.button("➕ Create Your First Resume"):

            st.session_state.page = "create"

            st.rerun()

        st.stop()

    st.write(
        f"Total resumes: **{len(resumes)}**"
    )

    for resume in resumes:

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [5, 1, 1]
            )

            with col1:

                st.subheader(
                    f"📄 {resume['name']}"
                )

                st.write(
                    f"**Position:** {resume['job_title'] or 'Not specified'}"
                )

                st.caption(
                    f"Last Updated: {resume['updated_at']}"
                )

            with col2:

                if st.button(
                    "✏️ Edit",
                    key=f"edit_{resume['id']}"
                ):

                    st.session_state.edit_id = resume["id"]
                    st.session_state.page = "create"

                    st.rerun()

            with col3:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{resume['id']}"
                ):

                    delete_resume(
                        resume["id"],
                        st.session_state.user_id
                    )

                    st.success(
                        "Resume deleted."
                    )

                    st.rerun()

    st.stop()


# ============================================================
# CREATE / EDIT PAGE
# ============================================================

editing = (
    st.session_state.edit_id is not None
)

old_resume = None

if editing:

    old_resume = get_resume(
        st.session_state.edit_id,
        st.session_state.user_id
    )

    if old_resume is None:

        st.error(
            "Resume not found."
        )

        st.session_state.edit_id = None

        st.stop()


if editing:

    st.title("✏️ Edit / Update Resume")

    st.info(
        "Update your information and click "
        "**Update Resume** to save the changes."
    )

else:

    st.title("🌟 AI Resume Generator")

    st.write(
        "Create a professional resume using AI."
    )


# ============================================================
# DEFAULT VALUES FOR EDIT MODE
# ============================================================

def old_value(column, default=""):

    if editing and old_resume:

        return old_resume[column] or default

    return default


# ============================================================
# EXAMPLE DATA
# ============================================================

job_title_options = [
    "",
    "Data Analyst",
    "Software Engineer",
    "Product Manager",
    "Marketing Specialist",
    "Business Analyst",
    "UX Designer",
    "Project Manager",
    "Data Scientist",
    "Sales Executive"
]

summary_examples = {
    "": "",
    "Data Analyst":
        "Results-driven Data Analyst with 3+ years of experience transforming complex data into actionable insights. Proven expertise in SQL, Python, and data visualization tools.",
    "Software Engineer":
        "Innovative Software Engineer with 4+ years of experience building scalable web applications. Skilled in full-stack development, cloud technologies, and agile methodologies.",
    "Business Analyst":
        "Strategic Business Analyst with expertise in process optimization and data-driven decision making. Strong analytical skills with proven track record of improving operational efficiency.",
    "Marketing Specialist":
        "Creative Marketing Specialist with 3+ years driving brand awareness and customer engagement. Expert in digital marketing, content strategy, and analytics.",
    "Data Scientist":
        "Analytical Data Scientist with expertise in machine learning and statistical modeling. Experienced in developing predictive models and deriving insights from complex datasets."
}

skills_examples = {
    "":
        "",
    "Data Analyst":
        "Python, SQL, Excel, Power BI, Tableau, Data Visualization, Statistical Analysis, ETL",
    "Software Engineer":
        "Python, Java, JavaScript, React, Node.js, AWS, Docker, Git, REST APIs, SQL, MongoDB",
    "Business Analyst":
        "SQL, Excel, Power BI, Tableau, Business Process Modeling, Requirements Gathering, Agile, JIRA",
    "Marketing Specialist":
        "Digital Marketing, SEO/SEM, Google Analytics, Social Media Marketing, Content Strategy",
    "Data Scientist":
        "Python, R, Machine Learning, Deep Learning, TensorFlow, Scikit-learn, SQL, NLP",
    "Project Manager":
        "Project Management, Agile/Scrum, JIRA, Risk Management, Stakeholder Communication",
    "UX Designer":
        "Figma, Adobe XD, Sketch, User Research, Wireframing, Prototyping, Usability Testing"
}

education_examples = {
    "":
        "",
    "Computer Science":
        "Bachelor of Science in Computer Science\nXYZ University, 2020-2024\nGPA: 3.8/4.0",
    "Business Administration":
        "Bachelor of Business Administration\nABC University, 2019-2023\nGPA: 3.7/4.0",
    "Data Science":
        "Master of Science in Data Science\nTech University, 2022-2024\nGPA: 3.9/4.0",
    "Engineering":
        "Bachelor of Engineering in Software Engineering\nState University, 2018-2022\nGPA: 3.6/4.0",
    "MBA":
        "Master of Business Administration (MBA)\nBusiness School, 2023-2025"
}

cert_examples = {
    "":
        "",
    "Data Analytics":
        "Google Data Analytics Professional Certificate (2024)\nMicrosoft Certified: Azure Data Fundamentals (2023)",
    "Cloud/DevOps":
        "AWS Certified Solutions Architect - Associate (2024)\nDocker Certified Associate (2023)",
    "Project Management":
        "Project Management Professional (PMP) (2024)\nCertified Scrum Master (CSM) (2023)",
    "Data Science":
        "TensorFlow Developer Certificate (2024)\nIBM Data Science Professional Certificate (2023)"
}

exp_examples = {
    "":
        "",
    "Data Analyst":
        """Data Analyst Intern | Tech Solutions Inc. | June 2023 - Present
- Analyzed sales data using SQL and Python
- Created interactive dashboards in Power BI
- Automated data cleaning processes

Student Data Analytics Project | University Project | Jan 2023 - May 2023
- Built predictive model using Python
- Presented findings to faculty panel""",

    "Software Engineer":
        """Junior Software Engineer | Tech Startup Inc. | May 2023 - Present
- Developed full-stack features using React and Node.js
- Optimized database queries
- Implemented automated testing

Full-Stack Developer | University Project | Jan 2023 - May 2023
- Built web application using MERN stack
- Implemented authentication system""",

    "Marketing Specialist":
        """Digital Marketing Specialist | GrowthMark Agency | Jan 2022 - Present
- Managed digital marketing campaigns
- Increased website traffic through SEO
- Managed social media campaigns

Marketing Coordinator | StartupCo | Jun 2020 - Dec 2021
- Coordinated product launch campaigns
- Created content strategy""",

    "Business Analyst":
        """Business Analyst | Enterprise Solutions Corp | Feb 2022 - Present
- Led requirements gathering
- Identified process improvements
- Created business requirements documents

Junior Business Analyst | Consulting Partners LLC | Jul 2020 - Jan 2022
- Analyzed business processes
- Conducted gap analysis"""
}

achievement_examples = {
    "":
        "",
    "Academic":
        "Dean's List - All 4 years\nUniversity Merit Scholarship Recipient",
    "Professional":
        "Employee of the Year 2023\nExceeded sales targets by 150%",
    "Competitions":
        "1st Place - National Data Science Hackathon 2024\n2nd Place - University Coding Competition",
    "Combined":
        "Top Performer Award\nPublished research paper\nBest Data Visualization Award"
}


# ============================================================
# RESUME FORM
# ============================================================

with st.form(
    "resume_form",
    clear_on_submit=False
):

    st.subheader("📝 Personal Information")

    col1, col2 = st.columns(2)

    with col1:

        name = st.text_input(
            "Full Name*",
            value=old_value("name"),
            placeholder="John Doe"
        )

    with col2:

        old_job = old_value("job_title")

        job_index = (
            job_title_options.index(old_job)
            if old_job in job_title_options
            else 0
        )

        job_title = st.selectbox(
            "Job Title / Position",
            job_title_options,
            index=job_index
        )

    col3, col4, col5 = st.columns(3)

    with col3:

        email = st.text_input(
            "Email",
            value=old_value("email"),
            placeholder="john@example.com"
        )

    with col4:

        phone = st.text_input(
            "Phone",
            value=old_value("phone"),
            placeholder="+91 9876543210"
        )

    with col5:

        locations = [
            "Choose from list",
            "Mumbai",
            "Pune",
            "Delhi",
            "Bangalore",
            "Chennai",
            "Other"
        ]

        old_location = old_value("location")

        if old_location in locations:
            location_index = locations.index(old_location)
            custom_location = ""
        else:
            location_index = 6 if old_location else 0
            custom_location = old_location

        location_option = st.selectbox(
            "Select Location",
            locations,
            index=location_index
        )

        if location_option == "Other":

            location = st.text_input(
                "Enter Custom Location",
                value=custom_location
            )

        else:

            location = (
                ""
                if location_option == "Choose from list"
                else location_option
            )

    col6, col7 = st.columns(2)

    with col6:

        linkedin = st.text_input(
            "LinkedIn",
            value=old_value("linkedin"),
            placeholder="linkedin.com/in/johndoe"
        )

    with col7:

        portfolio = st.text_input(
            "Portfolio / Website",
            value=old_value("portfolio"),
            placeholder="johndoe.com"
        )

    st.markdown("---")

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    st.subheader("👤 Professional Summary")

    old_summary = old_value("summary")

    summary_key = st.selectbox(
        "Choose Summary Example",
        list(summary_examples.keys())
    )

    if old_summary and editing:

        summary = st.text_area(
            "Professional Summary",
            value=old_summary,
            height=100
        )

    elif summary_key:

        summary = st.text_area(
            "Edit or use as-is",
            value=summary_examples[summary_key],
            height=100
        )

    else:

        summary = st.text_area(
            "Professional Summary",
            height=100
        )

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    st.subheader("🛠️ Skills")

    old_skills = old_value("skills")

    skills_key = st.selectbox(
        "Choose Skills Example",
        list(skills_examples.keys())
    )

    if old_skills and editing:

        skills = st.text_area(
            "Skills*",
            value=old_skills,
            height=80
        )

    elif skills_key:

        skills = st.text_area(
            "Edit or use as-is",
            value=skills_examples[skills_key],
            height=80
        )

    else:

        skills = st.text_area(
            "Skills*",
            height=80,
            placeholder="Python, SQL, Excel, Power BI..."
        )

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    st.subheader("🎓 Education")

    old_education = old_value("education")

    education_key = st.selectbox(
        "Choose Education Example",
        list(education_examples.keys())
    )

    if old_education and editing:

        education = st.text_area(
            "Education*",
            value=old_education,
            height=120
        )

    elif education_key:

        education = st.text_area(
            "Edit or use as-is",
            value=education_examples[education_key],
            height=120
        )

    else:

        education = st.text_area(
            "Education*",
            height=120
        )

    # --------------------------------------------------------
    # CERTIFICATIONS
    # --------------------------------------------------------

    st.subheader("🏆 Certifications")

    old_certifications = old_value(
        "certifications"
    )

    cert_key = st.selectbox(
        "Choose Certification Example",
        list(cert_examples.keys())
    )

    if old_certifications and editing:

        certifications = st.text_area(
            "Certifications",
            value=old_certifications,
            height=80
        )

    elif cert_key:

        certifications = st.text_area(
            "Edit or use as-is",
            value=cert_examples[cert_key],
            height=80
        )

    else:

        certifications = st.text_area(
            "Certifications",
            height=80
        )

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    st.subheader("💼 Experience / Projects")

    old_experience = old_value(
        "experience"
    )

    exp_key = st.selectbox(
        "Choose Experience Example",
        list(exp_examples.keys())
    )

    if old_experience and editing:

        experience = st.text_area(
            "Work Experience / Projects*",
            value=old_experience,
            height=220
        )

    elif exp_key:

        experience = st.text_area(
            "Edit or use as-is",
            value=exp_examples[exp_key],
            height=220
        )

    else:

        experience = st.text_area(
            "Work Experience / Projects*",
            height=180
        )

    # --------------------------------------------------------
    # LANGUAGES AND INTERESTS
    # --------------------------------------------------------

    col8, col9 = st.columns(2)

    language_options = [
        "",
        "English (Native), Hindi (Native)",
        "English (Native), Spanish (Fluent)",
        "English (Fluent), French (Intermediate)",
        "English (Native), Mandarin (Professional)"
    ]

    interest_options = [
        "",
        "Data Science, Tech Blogging, Photography",
        "Open Source Contribution, Hiking, Chess",
        "Machine Learning Research, Marathon Running",
        "UI/UX Design, Travel, Cooking"
    ]

    with col8:

        old_languages = old_value(
            "languages"
        )

        language_options_with_old = language_options.copy()

        if (
            old_languages
            and old_languages not in language_options_with_old
        ):
            language_options_with_old.insert(
                0,
                old_languages
            )

        languages = st.selectbox(
            "Languages",
            language_options_with_old
        )

    with col9:

        old_interests = old_value(
            "interests"
        )

        interest_options_with_old = interest_options.copy()

        if (
            old_interests
            and old_interests not in interest_options_with_old
        ):
            interest_options_with_old.insert(
                0,
                old_interests
            )

        interests = st.selectbox(
            "Interests / Hobbies",
            interest_options_with_old
        )

    # --------------------------------------------------------
    # ACHIEVEMENTS
    # --------------------------------------------------------

    st.subheader("🥇 Achievements / Awards")

    old_achievements = old_value(
        "achievements"
    )

    achievement_key = st.selectbox(
        "Choose Achievement Example",
        list(achievement_examples.keys())
    )

    if old_achievements and editing:

        achievements = st.text_area(
            "Achievements / Awards",
            value=old_achievements,
            height=80
        )

    elif achievement_key:

        achievements = st.text_area(
            "Edit or use as-is",
            value=achievement_examples[achievement_key],
            height=80
        )

    else:

        achievements = st.text_area(
            "Achievements / Awards",
            height=80
        )

    # --------------------------------------------------------
    # STYLE + TEMPLATE
    # --------------------------------------------------------

    st.markdown("---")

    col10, col11 = st.columns(2)

    style_options = [
        "Concise",
        "Creative",
        "ATS-friendly"
    ]

    template_options = [
        "Classic",
        "Modern",
        "Elegant"
    ]

    with col10:

        old_style = old_value(
            "style",
            "Concise"
        )

        style_index = (
            style_options.index(old_style)
            if old_style in style_options
            else 0
        )

        style = st.selectbox(
            "Resume Style",
            style_options,
            index=style_index
        )

    with col11:

        old_template = old_value(
            "template",
            "Classic"
        )

        template_index = (
            template_options.index(old_template)
            if old_template in template_options
            else 0
        )

        template = st.selectbox(
            "PDF Template",
            template_options,
            index=template_index
        )

    # --------------------------------------------------------
    # SUBMIT BUTTON
    # --------------------------------------------------------

    if editing:

        submitted = st.form_submit_button(
            "🔄 Update Resume",
            use_container_width=True
        )

    else:

        submitted = st.form_submit_button(
            "✨ Generate & Save Resume",
            use_container_width=True
        )


# ============================================================
# GENERATE / UPDATE
# ============================================================

if submitted:

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name.strip():

        st.error(
            "⚠️ Please enter your full name."
        )

        st.stop()

    if not skills.strip():

        st.error(
            "⚠️ Please enter your skills."
        )

        st.stop()

    if not education.strip():

        st.error(
            "⚠️ Please enter your education."
        )

        st.stop()

    if not experience.strip():

        st.error(
            "⚠️ Please enter your experience/projects."
        )

        st.stop()

    if use_ai and not api_key:

        st.error(
            "⚠️ Please enter your Gemini API key "
            "or disable AI Generation."
        )

        st.stop()

    # --------------------------------------------------------
    # COLLECT DATA
    # --------------------------------------------------------

    resume_data = {

        "name": name,
        "job_title": job_title,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "portfolio": portfolio,
        "summary": summary,
        "skills": skills,
        "education": education,
        "certifications": certifications,
        "experience": experience,
        "languages": languages,
        "interests": interests,
        "achievements": achievements,
        "style": style,
        "template": template
    }

    # --------------------------------------------------------
    # GENERATE RESUME
    # --------------------------------------------------------

    with st.spinner(
        "✨ Generating your professional resume..."
    ):

        try:

            resume_text = generate_resume(

                name=name,
                job_title=job_title,
                email=email,
                phone=phone,
                location=location,
                linkedin=linkedin,
                portfolio=portfolio,
                summary=summary,
                skills=skills,
                education=education,
                certifications=certifications,
                experience=experience,
                languages=languages,
                interests=interests,
                achievements=achievements,
                style=style,
                use_ai=use_ai,
                api_key=api_key if use_ai else None
            )

        except Exception as e:

            st.error(
                f"❌ Error generating resume: {str(e)}"
            )

            st.info(
                "Try disabling AI Generation if "
                "there is a Gemini API problem."
            )

            st.stop()

    # --------------------------------------------------------
    # SAVE OR UPDATE DATABASE
    # --------------------------------------------------------

    if editing:

        update_resume(
            st.session_state.edit_id,
            st.session_state.user_id,
            resume_data,
            resume_text
        )

        st.success(
            "✅ Resume updated successfully!"
        )

    else:

        resume_id = save_resume(
            st.session_state.user_id,
            resume_data,
            resume_text
        )

        st.session_state.edit_id = resume_id

        st.success(
            "✅ Resume generated and saved successfully!"
        )

    st.session_state.generated_resume = resume_text


# ============================================================
# SHOW GENERATED RESUME
# ============================================================

if st.session_state.generated_resume:

    resume_text = st.session_state.generated_resume

    st.markdown("---")

    st.subheader("📄 Resume Preview")

    st.markdown(
        """
        <style>

        .resume-preview {
            background: white;
            padding: 35px;
            border-radius: 10px;
            border: 1px solid #ddd;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #222;
        }

        .resume-preview h1 {
            text-align: center;
            font-size: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }

        .resume-preview h2 {
            color: #2980b9;
            font-size: 20px;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
            margin-top: 25px;
        }

        .resume-preview p {
            margin: 8px 0;
        }

        .resume-preview li {
            margin-bottom: 6px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    formatted_resume = format_resume_for_display(
        resume_text
    )

    st.markdown(
        f"""
        <div class="resume-preview">
            {formatted_resume}
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # PLAIN TEXT
    # --------------------------------------------------------

    with st.expander("📝 View / Edit Generated Text"):

        edited_text = st.text_area(
            "Resume Text",
            value=resume_text,
            height=400,
            key="generated_text_editor"
        )

        if st.button(
            "💾 Save Text Changes",
            use_container_width=True
        ):

            if editing:

                update_resume(
                    st.session_state.edit_id,
                    st.session_state.user_id,
                    {
                        "name": name,
                        "job_title": job_title,
                        "email": email,
                        "phone": phone,
                        "location": location,
                        "linkedin": linkedin,
                        "portfolio": portfolio,
                        "summary": summary,
                        "skills": skills,
                        "education": education,
                        "certifications": certifications,
                        "experience": experience,
                        "languages": languages,
                        "interests": interests,
                        "achievements": achievements,
                        "style": style,
                        "template": template
                    },
                    edited_text
                )

                st.session_state.generated_resume = edited_text

                st.success(
                    "✅ Resume text updated!"
                )

                st.rerun()

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    st.subheader("📥 Download Resume")

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    pdf_name = f"resume_{timestamp}.pdf"

    try:

        with st.spinner(
            "📄 Creating PDF..."
        ):

            text_to_pdf(
                resume_text,
                filename=pdf_name,
                template=template
            )

        with open(
            pdf_name,
            "rb"
        ) as pdf_file:

            st.download_button(
                "⬇️ Download PDF Resume",
                data=pdf_file,
                file_name=pdf_name,
                mime="application/pdf",
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"❌ PDF creation error: {str(e)}"
        )

    # --------------------------------------------------------
    # EDIT AGAIN
    # --------------------------------------------------------

    if editing:

        if st.button(
            "📂 Back to My Resumes",
            use_container_width=True
        ):

            st.session_state.page = "my_resumes"
            st.session_state.edit_id = None
            st.session_state.generated_resume = None

            st.rerun()