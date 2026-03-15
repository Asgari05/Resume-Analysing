from flask import Flask, render_template, request
import PyPDF2
import docx
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------- Extract text from PDF --------
def extract_pdf(file_path):

    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

    return text


# -------- Extract text from DOCX --------
def extract_docx(file_path):

    doc = docx.Document(file_path)

    text = ""

    for para in doc.paragraphs:
        text += para.text

    return text


# -------- Resume Analyzer --------
def analyze_resume(text):

    text = text.lower()

    score = 50
    strengths = []
    weaknesses = []
    domains = []
    suggestions = []

    # Skill → Domain mapping
    skills = {
        "python": "Data Science / AI",
        "machine learning": "Artificial Intelligence",
        "html": "Web Development",
        "css": "Web Development",
        "javascript": "Web Development",
        "react": "Frontend Development",
        "sql": "Database Management",
        "excel": "Data Analysis"
    }

    # -------- Detect Strengths --------
    for skill in skills:

        if skill in text:

            strengths.append(
                f"The resume demonstrates knowledge in {skill}. "
                f"This indicates the candidate has practical understanding of this technology."
            )

            domains.append(skills[skill])

            score += 5

    # If no strengths found
    if not strengths:

        strengths.append(
            "The resume does not clearly highlight technical skills. "
            "Adding a dedicated skills section would improve the resume."
        )

    # -------- Weakness Detection --------
    if len(text) < 300:

        weaknesses.append(
            "The resume content is quite short and may not fully represent the candidate’s abilities."
        )

        suggestions.append(
            "Add more detailed descriptions about projects, skills, and achievements."
        )

        score -= 10

    if "project" not in text:

        weaknesses.append(
            "Projects are not clearly mentioned in the resume."
        )

        suggestions.append(
            "Include at least two projects describing the technologies used and the problem solved."
        )

        score -= 10

    if "experience" not in text:

        weaknesses.append(
            "Professional or internship experience is not visible in the resume."
        )

        suggestions.append(
            "Adding internship or freelance experience will strengthen the resume."
        )

    if not weaknesses:

        weaknesses.append(
            "The resume structure looks balanced without major weaknesses."
        )

    # -------- Domain Suggestion --------
    if not domains:

        domains.append(
            "General Software Development"
        )

    domains = list(set(domains))

    # -------- Improvement Suggestions --------
    if not suggestions:

        suggestions.append(
            "The resume is good but adding certifications, achievements, or internships can further improve it."
        )

    if score > 100:
        score = 100

    return score, strengths, weaknesses, domains, suggestions


# -------- Website Route --------
@app.route("/", methods=["GET", "POST"])
def index():

    result = None

    if request.method == "POST":

        file = request.files["resume"]

        if file:

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

            file.save(filepath)

            if file.filename.endswith(".pdf"):

                text = extract_pdf(filepath)

            elif file.filename.endswith(".docx"):

                text = extract_docx(filepath)

            else:

                text = ""

            score, strengths, weaknesses, domains, suggestions = analyze_resume(text)

            result = {
                "score": score,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "domains": domains,
                "suggestions": suggestions
            }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)