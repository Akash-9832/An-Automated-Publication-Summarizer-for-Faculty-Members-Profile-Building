from bs4 import BeautifulSoup
import requests

def scrapeCitationPage(citation_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    source = requests.get(citation_url, headers=headers)
    soup = BeautifulSoup(source.text, 'html.parser')
    
    paper_details = {}
    
    try:
        paper_title = soup.find('div', id="gsc_oci_title").find('a', class_ = "gsc_oci_title_link").text
    except:
        paper_title = "Not Available"
    paper_details["Title"] = paper_title.strip()
    
    try:
        published_paper_link = soup.find('div', id="gsc_oci_title").find('a', class_ = "gsc_oci_title_link").get('href')
    except:
        published_paper_link = "No Link Available"
    paper_details["Publication URL"] = published_paper_link
    
    try:
        user_img = soup.find('a', class_ = "gs_ibl").find('span', class_="gs_rimg").find('img').get('src')
    except:
        user_img = "No User Image"
    paper_details["User Image"] = user_img
    
    for item in soup.find_all("div", class_="gs_scl"):
        attribute = item.find("div", class_="gsc_oci_field").text
        value = item.find("div", class_="gsc_oci_value").text
        if attribute and value:
            paper_details[attribute.strip()] = value.strip()

    citations_element = soup.find("a", string=lambda x: x and "Cited by" in x)
    try:
        paper_details["Total Citations"] = citations_element.text.strip()
    except:
        paper_details["Total Citations"] = "Not Available"
    
    return paper_details

