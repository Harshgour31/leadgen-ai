import requests
import pandas as pd
from bs4 import BeautifulSoup
import re


# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def normalize_domain(url: str) -> str:
    """
    Normalize and clean a domain string.
    Removes http/https and trailing slashes.
    """
    if not url:
        return None
    cleaned = url.strip().lower()
    cleaned = re.sub(r"^https?://", "", cleaned)  # remove protocol
    return cleaned.split("/")[0]  # keep only the base domain


def is_valid_domain(domain: str) -> bool:
    """
    Simple domain validator using regex.
    """
    pattern = r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, domain))


def compute_ai_score(domain: str) -> int:
    """
    Fetch homepage text and count AI-related keywords.
    Returns a score between 0–5.
    """
    keywords = ["ai", "machine learning", "automation",
                "artificial intelligence", "data science"]
    try:
        response = requests.get(f"https://{domain}", timeout=5)
        if response.status_code != 200:
            return 0
        page_text = BeautifulSoup(response.text, "html.parser").get_text().lower()
        hits = sum(1 for word in keywords if word in page_text)
        return min(hits, 5)
    except Exception:
        return 0


def remove_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate rows by domain.
    """
    data["Domain"] = data["Domain"].apply(normalize_domain)
    return data.drop_duplicates(subset=["Domain"]).reset_index(drop=True)


# --------------------------------------------------------
# Main Workflow
# --------------------------------------------------------

def process_leads(input_list: list) -> pd.DataFrame:
    """
    Takes a list of company dicts with {name, domain}.
    Returns a DataFrame with domain checks and AI scores.
    """
    output = []
    for entry in input_list:
        domain = normalize_domain(entry.get("domain"))
        if not domain:
            continue
        output.append({
            "Company": entry.get("name"),
            "Domain": domain,
            "Domain Valid": is_valid_domain(domain),
            "AI Score (0-5)": compute_ai_score(domain)
        })
    df = pd.DataFrame(output)
    return remove_duplicates(df)


if __name__ == "__main__":
    # Example seed data (can be replaced with CSV input later)
    companies = [
        {"name": "OpenAI", "domain": "openai.com"},
        {"name": "Caprae Capital", "domain": "capraecapital.com"},
        {"name": "OpenAI Duplicate", "domain": "https://openai.com/"},
        {"name": "Invalid Example", "domain": "notarealdomain.abc"},
    ]

    results = process_leads(companies)
    results.to_csv("leads_output.csv", index=False)
    print("✔ Lead data processed and saved to leads_output.csv")
    print(results)
