# lead_ranker.py

# Define weights
TITLE_WEIGHT = 0.1
EMAIL_WEIGHT = 0.5
WEBSITE_WEIGHT = 0.4

def email_score(email_status: str) -> int:
    status = email_status.lower().strip()
    if status == "valid":
        return 100
    elif status == "catchall":
        return 60
    elif status == "disposable":
        return 40
    elif status == "unknown":
        return 30
    else:  # includes 'invalid', 'error', or anything else
        return 0

def website_score(website_status: str) -> int:
    status = website_status.lower().strip()
    if status == "real_business":
        return 100
    elif status == "placeholder":
        return 50
    else:  # 'junk_or_unclear', 'llm_error', or anything else
        return 0

def calculate_lead_score(title_score: int, email_status: str, website_status: str) -> float:
    e_score = email_score(email_status)
    w_score = website_score(website_status)

    final_score = (
        (title_score * TITLE_WEIGHT) +
        (e_score * EMAIL_WEIGHT) +
        (w_score * WEBSITE_WEIGHT)
    )

    return round(final_score, 2)