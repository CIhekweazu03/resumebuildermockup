# app.py

import streamlit as st
import boto3
import json
import os
from io import BytesIO
# Library for PDF text extraction
import PyPDF2
# Library for creating Word documents
from docx import Document
from docx.shared import Pt


# Set page configuration with custom title and favicon
st.set_page_config(
    page_title="Resume Builder",
    page_icon="NIWC_Atlantic_Logo.jpg"
)

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3 = boto3.client('s3')

# create the prompt to be used with the generate experience
def create_prompt(experience):
    prompt = f"""


Based on the following information provided under 'Work Experience:', generate the 'Experience' section of a professional resume. Reword and enhance upon the details to make them more compelling and suitable for inclusion in a professional resume.


Please format the output as follows:


### Experience ###
(Enhanced experience content here)


Do not include any personal information like name, contact details, or education.
Do not include any new numbers and percentages in terms of impact. The only quantification of impact should be whatever the user literally states.


Work Experience:
{experience}
"""

    return prompt
def generate_experience(prompt):
    try:
        # Knowledge base is currently using an s3 bucket with a good bit of info.
        knowledge_base_id = "FROEVHOMYY"
        model_arn = "amazon.titan-text-premier-v1:0" 

        # Construct the payload for the RetrieveAndGenerate API
        payload = {
            "input": {
                "text": prompt
            },
            "retrieveAndGenerateConfiguration": {
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": knowledge_base_id,
                    "modelArn": model_arn
                },
                "type": "KNOWLEDGE_BASE"
            }
        }

        # Make the API call to the RetrieveAndGenerate function
        response = bedrock.retrieve_and_generate(
            input=payload['input'],
            retrieveAndGenerateConfiguration=payload['retrieveAndGenerateConfiguration']
        )

        # Debugging: Display the full response for insight
        st.write("Full API Response:", response)

        # Extract the generated text from the response
        result = response.get('results', [])[0]  # Get the first result from the response
        generated_text = result.get('outputText', '')  # Extract the 'outputText' field

        return generated_text

    except Exception as e:
        st.error(f"An error occurred while using the RetrieveAndGenerate function: {e}")
        return ""

def parse_experience(experience_text):
    # Parse the AI-generated experience section
    lines = experience_text.splitlines()
    experience_content = ''
    start_parsing = False
    for line in lines:
        line = line.strip()
        if line == "### Experience ###":
            start_parsing = True
            continue
        elif start_parsing:
            experience_content += line + '\n'
    return experience_content.strip()

def format_skills(skills_input):
    # Format the skills as per user's request
    return skills_input.strip()

def create_resume_docx(full_name, email, phone, education, experience_content, skills_content):
    # Create a new Word document
    document = Document()

    # Add Name as a header
    name_paragraph = document.add_heading(full_name, level=0)
    name_paragraph.alignment = 1  # Center alignment

    # Add contact information
    contact_info = f"Email: {email}\nPhone: {phone}"
    contact_paragraph = document.add_paragraph(contact_info)
    contact_paragraph.alignment = 1  # Center alignment

    # Add Education section
    document.add_heading('Education', level=1)
    document.add_paragraph(education)

    # Add Experience section
    document.add_heading('Experience', level=1)
    document.add_paragraph(experience_content)

    # Add Skills section
    document.add_heading('Skills', level=1)
    skills_lines = skills_content.split('\n')
    for line in skills_lines:
        # Each line is a separate category
        line = "- " + line
        document.add_paragraph(line)

    # Save the document
    docx_io = BytesIO()
    document.save(docx_io)
    docx_io.seek(0)
    return docx_io

def main():
    st.title("NIWC-A AI Resume Builder Mockup")

    st.header("Personal Information")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    education = st.text_area("Education (e.g., Degree, University)")

    st.header("Work Experience")
    experience = st.text_area("Describe your work experience")

    st.header("Skills")
    skills = st.text_area("List your skills as per the format:\n- Please group together similar skills on one line and separate them with a comma.\n\n For separate skill categories, write on a new line.\n\nExample:\n\n\'Python, Java, R\'\n\n\'Leadership, Communication\'")

    submit = st.button("Generate Resume")

    if submit:
        if not all([full_name, email, phone, education, experience, skills]):
            st.error("Please fill in all the fields.")
        else:
            with st.spinner('Generating your resume...'):
                prompt = create_prompt(experience)
                experience_text = generate_experience(prompt)

            if experience_text:
                # Parse the AI-generated experience content
                experience_content = parse_experience(experience_text)

                if not experience_content:
                    st.error("Failed to parse the AI-generated content. Please try again.")
                else:
                    # Format the skills as per user's request
                    skills_content = format_skills(skills)

                    # Create the DOCX resume
                    docx_file = create_resume_docx(full_name, email, phone, education, experience_content, skills_content)

                    st.header("Your Generated Resume")
                    st.download_button(
                        'Download Resume',
                        data=docx_file,
                        file_name='resume.docx',
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    )
                    st.success("Your resume has been generated!")

                    # Display the text version of the resume
                    text_resume = f"""
Name: {full_name}
Email: {email}
Phone: {phone}
Education: {education}

Experience:
{experience_content}

Skills:
{skills_content}
"""
                    st.text_area("Text Version of Your Resume", text_resume, height=300)

if __name__ == "__main__":
    main()
