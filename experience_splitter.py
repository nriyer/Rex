import re

# Sample experience text for testing (replace with actual parsed "experience" section)
experience_text = """
Substance Abuse and Mental Health Administration, Department of HHS  
Budget Analyst Dec ‘23 - Mar ‘25

- Conducted data mining of critical human capital information across divisions to support strategic decision-making and hiring status evaluations, assessing effectiveness through comprehensive data analysis procedures to enhance workforce planning.

- Developed an Excel VBA-based incentive tracking system, integrating engagement analysis and survey design to assess incentive award effectiveness. Implemented automated validation checks and dynamic data processing workflows, increasing data accuracy by 85% and enhancing communication-engagement data insights for decision-making.

- Engineered a real-time Python-based payroll tracking system, integrating 10+ fund sources and 25 Lines of Accounting, leveraging SQL for data extraction and pandas for analysis, reducing reconciliation time by ~2 hours/month and improving payroll forecasting accuracy.

- Designed and optimized SharePoint-based data management processes, improving workflow automation and document version control for financial reporting.

- Conducted financial forecasting and variance analysis for a $165M payroll budget, leading to actionable FTE adjustments and full-year payroll projections, optimizing workforce planning and budget allocation.

- Developed Power BI dashboards to provide real-time insights into budget utilization, payroll trends, and workforce analytics, enabling data-driven decision-making.

- Facilitated cross-functional workshops with stakeholders to gather insights that informed the optimization of decision pathways, resulting in a 30% reduction in processing time for budget approvals.

- Partnered with data science teams to analyze user interactions and optimize AI algorithms, reducing budget forecasting errors by 15% and improving overall accuracy in financial planning.

- Ensured compliance with federal regulations and data privacy laws in all human capital reporting and workforce analytics processes, effectively managing deadlines to ensure timely and accurate reporting.
"""

def split_experience_section(text):
    """
    Improved splitter: detects various date formats and uses a 2-line window
    to group job entries (title, org, date, bullets).
    """
    lines = text.strip().split("\n")
    job_chunks = []
    current_chunk = []

    # Updated date pattern to match:
    # - Jan '20
    # - March 2022
    # - 2020 – 2023
    # - Embedded formats (e.g., Job Title — Jan 2020 - Feb 2023)
    date_pattern = re.compile(
        r"((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+['’]?\d{2,4})|"      # e.g. Jan '20 or March 2022
        r"(\d{4}\s*[-–—]\s*(Present|\d{2,4}))",                                              # e.g. 2020 – 2023
        flags=re.IGNORECASE
    )

    i = 0
    while i < len(lines):
        line = lines[i]

        # If we find a line that looks like it contains dates, we treat this as the start of a new job
        if date_pattern.search(line):
            # If we already have a job being built, save it
            if current_chunk:
                job_chunks.append("\n".join(current_chunk).strip())
                current_chunk = []

            # Look back up to 2 lines (to get org/title)
            backtrack_lines = []
            if i >= 2:
                backtrack_lines = [lines[i-2], lines[i-1]]
            elif i == 1:
                backtrack_lines = [lines[i-1]]
            current_chunk.extend(backtrack_lines)

        current_chunk.append(line)
        i += 1

    # Add last chunk if exists
    if current_chunk:
        job_chunks.append("\n".join(current_chunk).strip())

    return job_chunks


# Run test and print results
if __name__ == "__main__":
    chunks = split_experience_section(experience_text)
    for i, chunk in enumerate(chunks):
        print(f"\n--- Job {i+1} ---\n{chunk}\n")
