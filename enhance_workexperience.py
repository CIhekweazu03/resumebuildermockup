import boto3
import json
from io import BytesIO
import PyPDF2

def get_rag_data_from_pdf():
    s3 = boto3.client('s3')
    bucket_name = 'resume-builder-mockup-bucket'
    keys = ['Federal Resume Samples.pdf', 'sample-resume.pdf']
    combined_text = ''

    for key in keys:
        try:
            response = s3.get_object(Bucket=bucket_name, Key=key)
            pdf_content = response['Body'].read()
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            combined_text += text + '\n'
        except Exception as e:
            print(f"Error fetching or parsing PDF from S3 for {key}: {e}")
            continue
    
    return combined_text

def create_prompt(experience):
    rag_data = get_rag_data_from_pdf()
    prompt = f"""
Human:
You are a career advisor who is focused on helping students (high school or college) or recently graduated students improve their resumes.
Here's a good bit of information about resumes generally speaking and a few good examples of how resumes should read {rag_data}

Based on the following information provided under 'Work Experience:', generate the new 'Experience' section of the student's professional resume. Reword and enhance upon the details to make them more compelling and suitable for inclusion in a professional resume.

Please format the output as follows:

### Experience ###
(Enhanced experience content here)

Do not include any personal information like name, contact details, or education.
Do not include any new numbers and percentages in terms of impact. The only quantification of impact should be whatever the user literally states.
Do not create new sentences, independent/dependent clauses, or bullet points; rather improve what is already there.
Always err on the side of caution to not add new bullet points and experience that the user did not previously state.
Be articulate and succinct and do not use excessive jargon to fill in.
When necessary, fix grammatical errors that the user made inside of the work experience.
Finish any generated bullet points with a period.
Do not add any extra empty lines between the geneerated bullet points. Simply one newline between the bullet points to ensure they are on separate lines.
Your goal with this is to simply express what the user has done, rather than impress readers.
The potential reader is expected to have some level of technical expertise in whatever field, so do not overexplain or restate the obvious. Example, rather than saying the X programming language or Y framework you can just say the language or framework in question.

Work Experience:
{experience}
Assistant:
"""
    return prompt

def generate_experience(prompt):
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    try:
        request_body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50000,
            "temperature": 0.2,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            contentType='application/json',
            accept='application/json',
            body=request_body
        )
        response_body = json.loads(response['body'].read())
        content = response_body.get('content', [])
        if content and isinstance(content, list) and 'text' in content[0]:
            return content[0]['text']
        else:
            print("Unexpected response format from the model.")
            return ""
    except Exception as e:
        print(f"An error occurred while invoking the model: {e}")
        return ""

def parse_experience(experience_text):
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

def generate_enhanced_experience(experience):
    prompt = create_prompt(experience)
    generated_text = generate_experience(prompt)
    parsed_experience = parse_experience(generated_text)
    return parsed_experience

def create_bio_prompt(bio):
    rag_data = get_rag_data_from_pdf()
    prompt = f"""
Human:
You are a career advisor specializing in federal resumes, focusing on helping applicants create compelling professional summaries that align with federal resume standards.
Here's reference information about federal resumes and examples of effective professional summaries: {rag_data}

Based on the following information provided under 'Professional Summary:', generate an enhanced professional summary section suitable for a federal resume. Reword and improve the content while maintaining accuracy and federal resume formatting standards.

Please format the output as follows:

### Professional Summary ###
(Enhanced professional summary here)

Guidelines:
Do not include any personal information like name, contact details, or education.
Do not include any new numbers and percentages in terms of impact. The only quantification of impact should be whatever the user literally states.
Do not create new sentences, independent/dependent clauses, or bullet points; rather improve what is already there.
Always err on the side of caution to not add new bullet points and experience that the user did not previously state.
Be articulate and succinct and do not use excessive jargon to fill in.
When necessary, fix grammatical errors that the user made inside of the work experience.
Finish any generated bullet points with a period.
Do not add any extra empty lines between the geneerated bullet points. Simply one newline between the bullet points to ensure they are on separate lines.
Your goal with this is to simply express what the user has done, rather than impress readers.
The potential reader is expected to have some level of technical expertise in whatever field, so do not overexplain or restate the obvious. Example, rather than saying the X programming language or Y framework you can just say the language or framework in question.
Format as a cohesive paragraph rather than bullet points
End sentences with proper punctuation
Maintain a formal, professional tone appropriate for federal positions
Do not add new achievements or qualifications not mentioned in the original

Professional Summary:
{bio}
Assistant:
"""
    return prompt

def generate_bio(prompt):
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    try:
        request_body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50000,
            "temperature": 0.2,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            contentType='application/json',
            accept='application/json',
            body=request_body
        )
        response_body = json.loads(response['body'].read())
        content = response_body.get('content', [])
        if content and isinstance(content, list) and 'text' in content[0]:
            return content[0]['text']
        else:
            print("Unexpected response format from the model.")
            return ""
    except Exception as e:
        print(f"An error occurred while invoking the model: {e}")
        return ""

def parse_bio(bio_text):
    lines = bio_text.splitlines()
    bio_content = ''
    start_parsing = False
    for line in lines:
        line = line.strip()
        if line == "### Professional Summary ###":
            start_parsing = True
            continue
        elif start_parsing:
            bio_content += line + ' '
    return bio_content.strip()

def generate_enhanced_bio(bio):
    prompt = create_bio_prompt(bio)
    generated_text = generate_bio(prompt)
    parsed_bio = parse_bio(generated_text)
    return parsed_bio

if __name__ == "__main__":
    user_experience = """
    - Developed web applications using Python and Django
    - Collaborated with team members on various projects
    """
    enhanced_experience = generate_enhanced_experience(user_experience)
    print("Enhanced Experience Section:")
    print(enhanced_experience)


    user_bio = """
    Experienced software developer with 5 years in web development and cloud computing. 
    Skilled in Python, AWS, and agile methodologies. Led multiple successful projects 
    and mentored junior developers.
    """
    enhanced_bio = generate_enhanced_bio(user_bio)
    print("Enhanced Professional Summary:")
    print(enhanced_bio)
