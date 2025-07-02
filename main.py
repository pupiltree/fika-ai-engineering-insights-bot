from resume_parser import extract_text_from_pdf
from insight_generator import generate_insights

if __name__ == "__main__":
    resume_path = input("Enter path to your resume PDF: ")
    text = extract_text_from_pdf(resume_path)
    print("Generating insights...\n")
    output = generate_insights(text)
    print(output)
