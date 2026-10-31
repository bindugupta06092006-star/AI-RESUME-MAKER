import google.generativeai as genai
import streamlit as st
import os
from typing import Optional

# Configure Gemini AI
def configure_ai(api_key: Optional[str] = None):
    """Configure Google Gemini AI with API key"""
    if api_key:
        genai.configure(api_key=api_key)
    elif os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    else:
        # Will raise error if no API key is set
        pass

def generate_resume_with_ai(name, job_title="", email="", phone="", location="", linkedin="", portfolio="",
                           summary="", skills="", education="", certifications="", experience="", 
                           languages="", interests="", achievements="", style="Concise", api_key=None):
    """
    Generate professional resume using Google Gemini AI.
    style options: Concise, Creative, ATS-friendly
    """
    try:
        configure_ai(api_key)
        
        # Create AI model
        model = genai.GenerativeModel('gemini-pro')
        
        # Build contact info string
        contact_parts = []
        if email:
            contact_parts.append(f"Email: {email}")
        if phone:
            contact_parts.append(f"Phone: {phone}")
        if location:
            contact_parts.append(f"Location: {location}")
        if linkedin:
            contact_parts.append(f"LinkedIn: {linkedin}")
        if portfolio:
            contact_parts.append(f"Portfolio: {portfolio}")
        contact_info = " | ".join(contact_parts) if contact_parts else ""
        
        # Craft prompt based on style
        if style == "Concise":
            prompt = f"""You are a professional resume writer. Create a concise, impactful resume for {name}.

INPUT INFORMATION:
Job Title: {job_title or "Professional"}
Contact: {contact_info}
Summary: {summary or "Not provided - create one based on skills and experience"}
Skills: {skills}
Education: {education}
Certifications: {certifications or "None"}
Experience/Projects: {experience}
Languages: {languages or "None"}
Achievements: {achievements or "None"}
Interests: {interests or "None"}

INSTRUCTIONS:
Transform the input into a professional resume. DO NOT just repeat what was given - enhance it significantly.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

{name}
{job_title if job_title else ""}
{contact_info if contact_info else ""}

PROFESSIONAL SUMMARY
[Write 2-3 compelling lines that highlight key strengths and value]

SKILLS
- [List the skills in an organized, professional format with bullet points]

EDUCATION
- [Format the education professionally with bullet points]

{f'''CERTIFICATIONS
- [List certifications with bullet points]
''' if certifications else ""}

EXPERIENCE
- [Transform the experience/projects into 4-6 powerful bullet points. Each must:
  * Start with strong action verbs (Developed, Implemented, Led, Designed, Optimized, Architected, etc.)
  * Include specific metrics and numbers (increased by X%, managed Y users, processed Z records, reduced time by N%)
  * Focus on achievements and impact, NOT just descriptions
  * Sound professional and impressive]

{f'''ACHIEVEMENTS
- [Format achievements with bullet points]
''' if achievements else ""}

{f'''LANGUAGES
{languages}
''' if languages else ""}

CRITICAL: Enhance the experience section significantly. If the input is vague, create professional achievements based on the context. Add realistic metrics and quantifiable results."""

        elif style == "Creative":
            prompt = f"""You are a creative resume writer. Create an engaging, memorable resume for {name}.

INPUT INFORMATION:
Job Title: {job_title or "Professional"}
Contact: {contact_info}
Summary: {summary or "Not provided - create engaging one"}
Skills: {skills}
Education: {education}
Certifications: {certifications or "None"}
Experience/Projects: {experience}
Languages: {languages or "None"}
Achievements: {achievements or "None"}
Interests: {interests or "None"}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

{name}
{job_title if job_title else ""}
{contact_info if contact_info else ""}

PROFESSIONAL SUMMARY
[Write an engaging 3-4 line narrative about {name}'s expertise and passion]

SKILLS
- [Present skills in an interesting, organized way with bullet points]

EDUCATION
- [Format education details engagingly with bullet points]

{f'''CERTIFICATIONS
- [List certifications]
''' if certifications else ""}

EXPERIENCE
- [Transform into 5-7 compelling achievement bullets with dynamic action verbs, impressive metrics, and storytelling]

{f'''ACHIEVEMENTS & AWARDS
- [Format achievements]
''' if achievements else ""}

{f'''LANGUAGES
{languages}
''' if languages else ""}

{f'''INTERESTS
{interests}
''' if interests else ""}

CRITICAL: Make the experience section shine with professional polish and compelling descriptions."""

        elif style == "ATS-friendly":
            prompt = f"""You are an ATS optimization expert. Create a keyword-rich, ATS-compliant resume for {name}.

INPUT INFORMATION:
Job Title: {job_title or "Professional"}
Contact: {contact_info}
Summary: {summary or "Not provided - create keyword-rich one"}
Skills: {skills}
Education: {education}
Certifications: {certifications or "None"}
Experience/Projects: {experience}
Languages: {languages or "None"}
Achievements: {achievements or "None"}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

{name}
{job_title if job_title else ""}
{contact_info if contact_info else ""}

PROFESSIONAL SUMMARY
[3-4 lines packed with relevant keywords and value proposition]

SKILLS
- {skills}

EDUCATION
- [Clear format: Degree, Institution, Year]

{f'''CERTIFICATIONS
- [List certifications]
''' if certifications else ""}

EXPERIENCE
- [Transform into 6-8 ATS-optimized achievement bullets with action verbs, specific metrics, and keywords]

{f'''ACHIEVEMENTS
- [Format achievements]
''' if achievements else ""}

{f'''LANGUAGES
{languages}
''' if languages else ""}

CRITICAL: Heavily enhance the experience section with professional metrics and quantifiable results."""

        else:
            prompt = f"""Create a professional resume for {name}.

INPUT:
Job Title: {job_title}
Contact: {contact_info}
Summary: {summary}
Skills: {skills}
Education: {education}
Certifications: {certifications}
Experience: {experience}
Languages: {languages}
Achievements: {achievements}

FORMAT with all sections, enhance experience with metrics and professional language."""

        return response.text
        
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fallback to template-based generation
        return generate_resume_template(name, job_title, email, phone, location, linkedin, portfolio,
                                       summary, skills, education, certifications, experience,
                                       languages, interests, achievements, style)


def generate_resume_template(name, job_title="", email="", phone="", location="", linkedin="", portfolio="",
                            summary="", skills="", education="", certifications="", experience="",
                            languages="", interests="", achievements="", style="Concise"):
    """
    Fallback: Generate resume text using templates (non-AI version).
    """
    resume = f"{name}\n"
    if job_title:
        resume += f"{job_title}\n"
    
    # Contact info
    contact_parts = []
    if email:
        contact_parts.append(email)
    if phone:
        contact_parts.append(phone)
    if location:
        contact_parts.append(location)
    if linkedin:
        contact_parts.append(linkedin)
    if portfolio:
        contact_parts.append(portfolio)
    if contact_parts:
        resume += " | ".join(contact_parts) + "\n"

    resume += "\n"

    # Summary
    if summary:
        resume += f"PROFESSIONAL SUMMARY\n{summary}\n\n"
    
    # Skills
    resume += f"SKILLS\n"
    if "," in skills:
        for skill in skills.split(","):
            resume += f"- {skill.strip()}\n"
    else:
        resume += f"- {skills}\n"
    resume += "\n"
    
    # Education
    resume += f"EDUCATION\n- {education}\n\n"
    
    # Certifications
    if certifications:
        resume += f"CERTIFICATIONS\n- {certifications}\n\n"
    
    # Experience
    resume += f"EXPERIENCE\n- {experience}\n\n"
    
    # Achievements
    if achievements:
        resume += f"ACHIEVEMENTS\n- {achievements}\n\n"
    
    # Languages
    if languages:
        resume += f"LANGUAGES\n{languages}\n\n"
    
    # Interests
    if interests:
        resume += f"INTERESTS\n{interests}\n"

    return resume


def generate_resume(name, job_title="", email="", phone="", location="", linkedin="", portfolio="",
                   summary="", skills="", education="", certifications="", experience="",
                   languages="", interests="", achievements="", style="Concise", use_ai=True, api_key=None):
    """
    Main function to generate resume - uses AI by default, falls back to template.
    """
    if use_ai:
        return generate_resume_with_ai(name, job_title, email, phone, location, linkedin, portfolio,
                                      summary, skills, education, certifications, experience,
                                      languages, interests, achievements, style, api_key)
    else:
        return generate_resume_template(name, job_title, email, phone, location, linkedin, portfolio,
                                       summary, skills, education, certifications, experience,
                                       languages, interests, achievements, style)




