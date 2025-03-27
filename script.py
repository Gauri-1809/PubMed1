import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import csv, re, time, sys

EMAIL = "your.email@example.com"  # Replace with your email
KEYWORDS = ['pharma', 'biotech', 'inc', 'corp', 'ltd', 'llc', 'company']

def get_ids(query):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = f"?db=pubmed&term={urllib.parse.quote(query)}&retmax=10&retmode=xml&email={EMAIL}"
    data = urllib.request.urlopen(url + params).read()
    return [id.text for id in ET.fromstring(data).findall(".//Id")]

def get_details(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml&email={EMAIL}"
    data = urllib.request.urlopen(url).read()
    root = ET.fromstring(data)
    article = root.find(".//PubmedArticle")
    if article is None:
        return None

    title = article.findtext(".//ArticleTitle", "")
    date = article.findtext(".//PubDate/Year", "N/A")
    authors, affiliations, email = [], [], ""

    for a in article.findall(".//Author"):
        name = (a.findtext("ForeName", "") + " " + a.findtext("LastName", "")).strip()
        for aff in a.findall(".//AffiliationInfo/Affiliation"):
            text = aff.text or ""
            if any(k in text.lower() for k in KEYWORDS):
                if name not in authors:
                    authors.append(name)
                if text not in affiliations:
                    affiliations.append(text)
                if not email:
                    match = re.search(r"\S+@\S+", text)
                    if match:
                        email = match.group()

    if not authors:
        return None
    return [pmid, title, date, "; ".join(authors), "; ".join(affiliations), email]

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py \"search term\"")
        return
    query = sys.argv[1]
    ids = get_ids(query)
    results = []
    for pmid in ids:
        time.sleep(0.4)
        row = get_details(pmid)
        if row:
            results.append(row)

    if results:
        with open("results.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["PubmedID", "Title", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"])
            writer.writerows(results)
        print("✅ Saved to results.csv")
    else:
        print("⚠️ No relevant papers found.")

if __name__ == "__main__":
    main()
