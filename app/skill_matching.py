import io
import re
import zipfile
from xml.etree import ElementTree


KNOWN_TECH_SKILLS = [
    "Python",
    "Flask",
    "Django",
    "FastAPI",
    "SQL",
    "PostgreSQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "React",
    "JavaScript",
    "Java",
    "C++",
    "Git",
    "Linux",
    "TensorFlow",
    "PyTorch",
]


def normalize_skills(skills_text: str) -> set[str]:
    return {
        skill.strip().lower()
        for skill in skills_text.split(",")
        if skill and skill.strip()
    }


def format_skills(skills: set[str]) -> str:
    return ", ".join(sorted(skills))


def extract_skills_from_text(text: str) -> set[str]:
    if not text:
        return set()

    lower_text = text.lower()
    found = set()
    for skill in KNOWN_TECH_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, lower_text):
            found.add(skill.lower())
    return found


def _extract_pdf_text(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return ""

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except Exception:
        return ""


def _extract_docx_text(file_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx_zip:
            xml_bytes = docx_zip.read("word/document.xml")
    except Exception:
        return ""

    try:
        root = ElementTree.fromstring(xml_bytes)
        texts = [node.text for node in root.iter() if node.text]
        return "\n".join(texts)
    except Exception:
        return ""


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    lower_name = (filename or "").lower()
    if lower_name.endswith(".pdf"):
        return _extract_pdf_text(file_bytes)
    if lower_name.endswith(".docx"):
        return _extract_docx_text(file_bytes)
    return ""


def build_match_summary(user_skills_raw: str, required_skills_raw: str) -> dict | None:
    user_skills = normalize_skills(user_skills_raw or "")
    required_skills = normalize_skills(required_skills_raw or "")
    if not user_skills or not required_skills:
        return None

    matched = sorted(user_skills.intersection(required_skills))
    missing = sorted(required_skills.difference(user_skills))
    score = round((len(matched) / len(required_skills)) * 100)

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
    }
