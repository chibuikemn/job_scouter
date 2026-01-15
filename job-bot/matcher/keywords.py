def keyword_score(job_text, skills):
    score = sum(1 for skill in skills if skill.lower() in job_text.lower())
    return score / len(skills)

class KeywordMatcher:
    def __init__(self, keywords):
        self.keywords = keywords
    
    def match_job(self, job_description):
        matches = []
        for keyword in self.keywords:
            if keyword.lower() in job_description.lower():
                matches.append(keyword)
        return matches
    
    def calculate_score(self, job_description):
        return keyword_score(job_description, self.keywords)