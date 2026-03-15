from flask import Flask, render_template, request
import PyPDF2
import docx
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder automatically
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

    score = 50
    strengths = []
    weaknesses = []
    domains = []
    suggestions = []

    text = text.lower()

    keywords = {
        "python": "AI / Data Science",
        "machine learning": "Artificial Intelligence",
        "react": "Frontend Development",
        "html": "Web Development",
        "css": "Web Development",
        "javascript": "Web Development",
        "sql": "Database Management",
        "data analysis": "Data Science"
    }

    # -------- Strength Detection --------
    for key in keywords:

        if key in text:

            score += 5

            strengths.append(
                f"The resume highlights experience in {key}. "
                f"This skill is widely used in modern technology roles and shows strong technical capability."
            )

            domains.append(keywords[key])

    # -------- Weakness Detection --------
    if len(text) < 300:

        weaknesses.append(
            "The resume content appears to be short. "
            "A short resume may not fully represent the candidate’s skills and experience."
        )

        suggestions.append(
            "Add more details about projects, technical skills, and internships to strengthen the resume."
        )

        score -= 10

    if "project" not in text:

        weaknesses.append(
            "No projects are clearly mentioned in the resume. "
            "Projects are important to demonstrate practical implementation of technical knowledge."
        )

        suggestions.append(
            "Include 2–3 projects explaining the technologies used and the problem solved."
        )

        score -= 10

    if "experience" not in text:

        weaknesses.append(
            "The resume does not mention professional or internship experience. "
            "Recruiters often prefer candidates with real-world exposure."
        )

        suggestions.append(
            "Add internship experience, freelancing work, or practical training programs."
        )

    if "skills" not in text:

        suggestions.append(
            "Create a separate skills section listing programming languages, tools, and frameworks."
        )

    if "education" not in text:

        suggestions.append(
            "Add an education section mentioning degree, institution, and academic achievements."
        )

    if score > 100:
        score = 100

    return score, strengths, weaknesses, list(set(domains)), suggestions


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