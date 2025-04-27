import re

def extract_contact_info(resume_text):
    """Extract basic contact information from resume text."""
    contact_info = {
        'name': '',
        'email': '',
        'phone': '',
        'location': '',
        'linkedin': '',
        'github': '',
        'website': ''
    }
    
    lines = resume_text.split('\n')[:15]
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 2 and '@' not in line and not line.startswith(('http', 'www')):
            if not any(term in line.lower() for term in ['resume', 'cv', 'summary']):
                contact_info['name'] = line
                break

    for line in lines:
        if email := re.search(email_pattern, line):
            contact_info['email'] = email.group(0)
            break
        if phone := re.search(phone_pattern, line):
            contact_info['phone'] = phone.group(0)
            break

    for line in lines:
        if any(keyword in line.lower() for keyword in ['city', 'state', 'country', 'location', 'address']) or ',' in line:
            contact_info['location'] = line.strip()
            break

    for line in lines:
        line_lower = line.lower()
        if 'github' in line_lower and (github := re.search(r'github\.com/[\w-]+', line_lower)):
            contact_info['github'] = github.group(0)
        if 'linkedin' in line_lower and (linkedin := re.search(r'linkedin\.com/in/[\w-]+', line_lower)):
            contact_info['linkedin'] = linkedin.group(0)
        if any(domain in line_lower for domain in ['.com', '.org', '.net', '.io']) and 'http' in line_lower:
            if website := re.search(r'https?://[\w.-]+\.\w+[\w/.-]*', line_lower):
                contact_info['website'] = website.group(0)

    return contact_info
