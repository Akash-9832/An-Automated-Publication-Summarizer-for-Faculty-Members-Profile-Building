import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import streamlit as st
import dynamicWebScraping
from scrapeSecondPage import scrapeCitationPage
from groqSummarizer import generate_summary_response


driver_path = Service(".\chromedriver-win32\chromedriver.exe")
driver = webdriver.Chrome(service=driver_path)

def delayed_driver_quit(delay=10):
    def quit_driver():
        try:
            driver.quit()
        except Exception as e:
            print(f"Error closing driver: {e}")
    timer = threading.Timer(delay, quit_driver)
    timer.start()

def main():
    st.markdown("<h2 style='text-align: center;'>Scholarly</h2>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; font-style: italic;'>An Automated Publication Summarizer for Faculty Members' Profile Building</h5>", unsafe_allow_html=True)

    if 'userURL' not in st.session_state:
        st.session_state.userURL = ""
    userURL = st.text_input(
        label="Enter your Google Scholar profile URL:",
        placeholder="https://scholar.google.com/user",
        value=st.session_state.userURL
    )

    if st.button("Search My Papers"):
        if userURL:
            st.session_state.userURL = userURL
            st.session_state.userInfo = dynamicWebScraping.scrape_profile_details(driver, userURL)
            st.session_state.articles_list = dynamicWebScraping.scrape_articles(driver)
            delayed_driver_quit(delay=8)
            st.session_state.papers = [article['title'] for article in st.session_state.articles_list]
            st.success("Papers fetched successfully!")
        else:
            st.error("Please enter your correct profile URL.")

    if 'userInfo' in st.session_state:
        st.write(st.session_state.userInfo['name'])
        st.markdown("**About**")
        st.write(st.session_state.userInfo['bio'])
        st.markdown("**Areas of Interest**")
        st.write(st.session_state.userInfo['area_of_interests'])

    if 'papers' in st.session_state:
        selectedPaperToSum = st.selectbox("Select a Paper to Summarize:", st.session_state.papers)
        citation_url = next(
            (article['href'] for article in st.session_state.articles_list if article['title'] == selectedPaperToSum),
            None
        )
        st.session_state.selected_citation_url = citation_url

        if st.button("Generate Summary"):
            if citation_url:
                paper_details = scrapeCitationPage(citation_url)
                delayed_driver_quit(delay=3)
                summary = generate_summary_response(
                    paper_details["Title"],
                    paper_details.get("Description", "No abstract available."),
                    paper_details["Publication URL"]
                )
                st.markdown("### Summary:")
                st.write(summary)
                st.write("Authors: ", paper_details["Authors"])
                st.write("Publication Date: ", paper_details["Publication date"])
                st.write("Total citations: ", paper_details["Total Citations"])
                delayed_driver_quit(delay=3)
            else:
                st.error("Could not find citation URL.")
if __name__ == "__main__":
    main()
