
import google.generativeai as genai
import pymupdf
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


from .forms import CustomUserCreationForm, ResumeForm
from .models import Resume

import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)
# Step 2: Set up OpenAI API
#openai.config(api_key=settings.OPENAI_API_KEY)  # Replace with your OpenAI API key

#openai.api_key = settings.OPENAI_API_KEY  # ✅ Correct way to set API key


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('upload_resume')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            return redirect('analysis_result', resume_id=resume.id)
    else:
        form = ResumeForm()
    return render(request, 'resume_analyzer/upload_resume.html', {'form': form})



from django.utils.safestring import mark_safe

def analysis_result(request, resume_id):
    resume = Resume.objects.get(id=resume_id, user=request.user)
    try:
        doc = pymupdf.open(stream=resume.resume_file.read(), filetype="pdf")
        analysis = ""
        text = ""
        for page in doc:
            text += page.get_text()

        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Updated prompt with HTML and ATS score
        prompt = f"""
                    You are an expert HR analyst and AI-powered career coach. Analyze the following resume and provide a detailed, well-formatted, and visually appealing **HTML report** with the following sections.

                    Please include inline CSS styles to ensure the report looks professional, clean, and ready for browser or PDF rendering.

                    ---

                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background-color: #f9f9f9;
                            padding: 30px;
                            line-height: 1.6;
                            color: #333;
                        }}
                        h2 {{
                            background-color: #e3f2fd;
                            color: #0d47a1;
                            padding: 10px;
                            border-left: 5px solid #2196f3;
                            border-radius: 5px;
                        }}
                        ul {{
                            margin-left: 20px;
                            padding-left: 10px;
                        }}
                        li {{
                            margin-bottom: 8px;
                        }}
                        .highlight {{
                            background-color: #fff3cd;
                            padding: 5px;
                            border-left: 4px solid #ffc107;
                            border-radius: 4px;
                        }}
                        .score {{
                            font-size: 20px;
                            font-weight: bold;
                            color: #4caf50;
                        }}
                    </style>

                    <h2>✨ Professional Summary</h2>
                    <p class="highlight">Write a concise 3–5 line summary capturing the candidate's background, strengths, and goals.</p>

                    <h2>🌟 Key Strengths</h2>
                    <ul>
                    <li>List 3–4 standout strengths (e.g., analytical thinking, problem-solving, leadership).</li>
                    </ul>

                    <h2>🛠️ Areas for Improvement</h2>
                    <ul>
                    <li>List 2–3 practical suggestions to improve the resume (e.g., clarity, skill gaps, formatting).</li>
                    </ul>

                    <h2> 🔑 Top Skills Extracted</h2>
                    <ul>
                    <li>List 5–7 key technical and soft skills from the resume (e.g., Python, communication, teamwork).</li>
                    </ul>

                    <h2> 🎯 Job Role Recommendations</h2>
                    <p>Recommend 5 job roles tailored to the candidate's skills. For each, provide:</p>
                    <ul>
                    <li><b>Job Title</b></li>
                    <li><b>Fictional Tech Company</b></li>
                    <li><b>Location</b></li>
                    <li><b>Brief Job Description</b> (2–3 lines)</li>
                    <li><b>Why it Matches</b> (connect with resume skills and experience)</li>
                    </ul>

                    <h2> 📊 ATS Score</h2>
                    <p class="score">Give an estimated ATS score out of 100.</p>
                    <ul>
                    <li><b>Score Breakdown:</b> Keyword match, formatting, relevance, clarity.</li>
                    <li><b>Remarks:</b> 1–2 lines explaining the score and how it can be improved.</li>
                    </ul>

                    ---

                    only give the analysis 
"""
 # Use the improved prompt from above
        
        response = model.generate_content(prompt)
        #analysis = mark_safe(response.text)  # Mark the response as safe HTML
        raw_html = response.text.strip()

        # Remove markdown code block wrapper if present
        if raw_html.startswith("```html"):
            raw_html = raw_html.replace("```html", "", 1).strip()
        if raw_html.endswith("```"):
            raw_html = raw_html[:-3].strip()

        analysis = mark_safe(raw_html)


    except Exception as e:
        analysis = f"<p style='color: red;'>An error occurred during analysis: {e}</p>"

    return render(request, 'resume_analyzer/analysis_result.html', {'analysis': analysis})

'''
@login_required
def analysis_result(request, resume_id):
    resume = Resume.objects.get(id=resume_id, user=request.user)
    try:
        doc = pymupdf.open(stream=resume.resume_file.read(), filetype="pdf")
        analysis =" "
        text = ""
        for page in doc:
            text += page.get_text()

        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
         You are an expert HR analyst and career coach. Your task is to analyze a resume and provide job recommendations.
         
        
        Please perform the following actions and provide the output :
        1.  **Resume Analysis**:
            -   Write a professional summary.
            -   Identify 3-4 key strengths.
            -   Suggest 2-3 actionable areas for improvement.
            -   Extract at least 5-7 relevant technical and soft skills as keywords.
        2.  **Job Recommendations**:
            -   Provide a list of 5 suitable job recommendations.
            -   For each job, include the title, a fictional tech company, location, a brief description, and a reason why it matches the analyzed skills.
    
        Resume Text:
        {text}
        """
        response = model.generate_content(prompt)
        analysis = response.text
        
    except Exception as e:
        analysis = f"An error occurred during analysis: {e}"

    return render(request, 'resume_analyzer/analysis_result.html', {'analysis': analysis})


login_required
def analysis_result(request, resume_id):
    resume = Resume.objects.get(id=resume_id, user=request.user)
    try:
        doc = pymupdf.open(stream=resume.resume_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()

        #model = genai.GenerativeModel('gemini-1.0-pro')
        prompt = f"""
        Analyze the following resume and provide:
        1.  A summary of the candidate's profile.
        2.  Key skills identified.
        3.  Areas for improvement.
        4.  Three tailored job recommendations with brief descriptions of why they are a good fit.

        Resume Text:
        {text}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are an expert career analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Step 5: Extract and print the response
        analysis = response['choices'][0]['message']['content']
    


    except Exception as e:
        analysis = f"An error occurred during analysis: {e}"

    return render(request, 'resume_analyzer/analysis_result.html', {'analysis': analysis})'''
    
def logout_view(request):
    logout(request)  # 👈 Automatically handles is_authenticated
    return redirect('login')
