import openai
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

KEYWORDS = ['policy', 'regulation', 'order', 'guideline', 'notification', 'amendment', 'circular', 'draft']
MAX_PAGES = 5

def load_agency_urls(path='agencies.xlsx'):
    df = pd.read_excel(path)
    df = df[['Agency/Platform Name', 'Website']].dropna()
    df.columns = ['Agency Name', 'URL']
    return df.to_dict(orient='records')

def fetch_policy_related_links(base_url):
    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            full_url = urljoin(base_url, href)
            if any(kw in href.lower() for kw in KEYWORDS) and urlparse(full_url).netloc in urlparse(base_url).netloc:
                links.add(full_url)
        links = list(links)[:MAX_PAGES]
        links.insert(0, base_url)
        return links
    except:
        return []

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join([p.get_text(strip=True) for p in soup.find_all(['p', 'li'])])
        return text[:3000]
    except:
        return ""

def summarize_text_openai(text, agency):
    try:
        prompt = f"Summarize this update from {agency} related to renewable energy policy or regulation:\n{text}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.5,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Summarization failed: {e}"

def generate_summary(openai_api_key):
    openai.api_key = openai_api_key
    results = {}
    agencies = load_agency_urls()
    for agency in agencies:
        agency_name = agency['Agency Name']
        base_url = agency['URL']
        links = fetch_policy_related_links(base_url)
        summaries = []
        for link in links:
            text = extract_text_from_url(link)
            if any(kw in text.lower() for kw in KEYWORDS):
                summary = summarize_text_openai(text, agency_name)
                summaries.append(f"{link}\n{summary}")
        results[agency_name] = summaries
    return results