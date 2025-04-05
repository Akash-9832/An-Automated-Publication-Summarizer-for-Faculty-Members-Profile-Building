from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time


def scrape_profile_details(driver, userURL):
    driver.get(userURL)
    time.sleep(5)
    name = driver.find_element(By.ID, "gsc_prf_in").text
    bio = driver.find_element(By.CLASS_NAME, "gsc_prf_il").text
    area_of_interests = driver.find_elements(By.CLASS_NAME, "gsc_prf_inta.gs_ibl")
    interest=[]
    for element in area_of_interests:
        interest.append(element.text)
    return {"name": name, "bio": bio, "area_of_interests": ", ".join(interest)}

def scrape_articles(driver):
    articles = []
    seen_links = set()
    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gsc_a_b"))
        )
        rows = driver.find_elements(By.CLASS_NAME, "gsc_a_tr")
        for row in rows:
            title_element = row.find_element(By.CLASS_NAME, "gsc_a_t")
            title = title_element.find_element(By.TAG_NAME, "a").text
            href = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            if href not in seen_links:
                articles.append({"title": title, "href": href})
                seen_links.add(href)
        try:
            show_more_button = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[12]/div[2]/div/div[4]/form/div[2]/div/button'))
            )
            show_more_button.click()
            time.sleep(4)
        except Exception:
            print("No more 'SHOW MORE' button or all articles loaded.")
            break
    return articles


if __name__ == "__main__":
    driver_path = Service(".\chromedriver-win32\chromedriver.exe")
    driver = webdriver.Chrome(service=driver_path)
    userURL = "https://scholar.google.com/citations?hl=en&user=so5yfkYAAAAJ"
    try:
        profile_info = scrape_profile_details(driver, userURL)
        print(f"Profile Info: {profile_info}")
        articles_list = scrape_articles(driver)
        print("\nFetched Articles:")
        for i, article in enumerate(articles_list, 1):
            # print(f"{i}. {article['title']} - {article['href']}")
            print(article['title'])
    finally:
        driver.quit()