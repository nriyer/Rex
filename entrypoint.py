# === entrypoint.py ===

from workflow import run_resume_enhancement_pipeline
from Archive.parsing_module import extract_text_pdfplumber

# === Step 1: Load resume (PDF)
resume_path = "docs/sample_resume.pdf"
resume_text = extract_text_pdfplumber(resume_path)

# === Step 2: Paste or load job posting
job_posting = """
People Data Analyst:

As a People Data Analyst, you will play a critical role in CAVA’s People & Culture function, specifically within the Total Rewards team. This role is responsible for producing regular reporting and data analysis, key in supporting strategic decision-making across People & Culture, while also collaborating with cross-functional teams across the organization. Your insights will help drive equitable, data-driven, and competitive strategies to attract and retain top talent. This role will provide data backed recommendations to help drive workforce strategy and support industry best practices.



What You’ll Do: 

Develop Periodic Reporting: Assist in creating and enhancing daily reporting to support various business areas.
Audit our People Data: Transform raw data so that it can be used in creating reports, maintaining reports, and summarizing results associated with our audits.
Interpret our People Data: Identify trends in data, comparing to both internal and external benchmarks.
Collaborate with Talent Acquisition & HR: Partner with recruiting and HR teams to merge data from outside of our HRIS systems to provide new insights and assist in creating new metrics.
Assist in Cross-Functional Analysis: Develop expertise in the organization’s people data and how it can be leveraged across other areas of the organization.
Maintain People Analytics Dashboards: Assist in dashboard maintenance and development.
Measure and Track Impact: Identify dates associated with initiatives to inform the business of the results of initiatives.


The Qualifications:

Bachelor’s degree in Human Resources, Business, Finance, Statistics, or a related field.
2+ years of experience in HR analytics, or data analysis in a corporate environment.
Proficiency in Excel (advanced), HRIS systems, and data visualization tools (e.g., Tableau, Power BI).
Experience working with SQL, Python, or another programming language preferred.
"""

# === Step 3: Run the enhancement pipeline
final_resume, score_report = run_resume_enhancement_pipeline(resume_text, job_posting)

# === Step 4: Export enhanced resume to .txt
with open("enhanced_resume.txt", "w", encoding="utf-8") as f:
    f.write(final_resume)

# === Step 5: Export score report to .txt
from pprint import pformat

with open("score_report.txt", "w", encoding="utf-8") as f:
    f.write("SCORE REPORT\n")
    f.write("============\n\n")
    f.write(pformat(score_report))

print("✅ Resume enhancement complete.")
print("📄 Output written to: enhanced_resume.txt")
print("📊 Score report written to: score_report.txt")
