import threading
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import streamlit as st
import dynamicWebScraping
from scrapeSecondPage import scrapeCitationPage
from groqSummarizer import generate_summary_response
from generateSummary import generate_summary
from emailSummary import user_config


driver_path = Service(".\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=driver_path)

def delayed_driver_quit(delay=4):
    def quit_driver():
        try:
            driver.quit()
        except Exception as e:
            print(f"Error closing driver: {e}")
    timer = threading.Timer(delay, quit_driver)
    timer.start()

def is_valid_gs_url(url):
    pattern = r"^(https?://)?scholar\.google\.com/"
    return re.match(pattern, url) is not None

def excel_exporter(userURL):
    # Step 1: Scrape user info and articles
    userInfo = dynamicWebScraping.scrape_profile_details(driver, userURL)
    articles_list = dynamicWebScraping.scrape_articles(driver)
    userName = userInfo['name']

    # Step 2: Load or create the Excel file
    file_name = 'researcher_db.xlsx'
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
    else:
        df = pd.DataFrame(columns=['name', 'profile_url', 'paper_title', 'year'])

    # Step 3: Filter for existing entries of this user
    existing_user_df = df[df['profile_url'] == userURL]

    # Step 4: Prepare a list for new entries
    new_rows = []

    for article in articles_list:
        title = article['title']
        year = article['year']

        # Check if this (title, year) already exists for this user
        if not ((existing_user_df['paper_title'] == title) & (existing_user_df['year'] == year)).any():
            new_rows.append({
                'name': userName,
                'profile_url': userURL,
                'paper_title': title,
                'year': year
            })

    # Step 5: Append new entries and save
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(file_name, index=False)
        print(f"{len(new_rows)} new records added for user: {userName}")
    else:
        print(f"No new records found for user: {userName}")

def view_stat(user_profile_url):
    df = pd.read_excel("researcher_db.xlsx")
    # Ensure 'profile_url' column exists
    if 'profile_url' not in df.columns:
        st.error("Missing 'profile_url' column in Excel file.")
        return
    # Filter the DataFrame for the given user's profile URL
    user_df = df[df['profile_url'] == user_profile_url]
    if user_df.empty:
        st.warning("No records found for this user.")
        return
    # Drop NA and convert year to integer
    user_df = user_df.dropna(subset=['year'])
    user_df['year'] = user_df['year'].astype(int)
    # Count publications by year
    yearly_counts = user_df['year'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(yearly_counts.index.astype(str), yearly_counts.values, color='skyblue')
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Publications")
    ax.set_title("Year-wise Publication Statistics")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

def main():
    if "ask_email" not in st.session_state:
        st.session_state.ask_email = False

    st.markdown("<h2 style='text-align: center;'>Scholarly</h2>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; font-style: italic;'>An Automated Publication Summarizer for Faculty Members' Profile Building</h5>", unsafe_allow_html=True)

    if 'userURL' not in st.session_state:
        st.session_state.userURL = ""
    userURL = st.text_input(
        label="Enter your Google Scholar profile URL:",
        placeholder="https://scholar.google.com/user",
        value=st.session_state.userURL
    )

    if userURL and is_valid_gs_url(userURL):
        excel_exporter(userURL)
        if st.button("Search My Papers"):
            st.session_state.userURL = userURL
            st.session_state.userInfo = dynamicWebScraping.scrape_profile_details(driver, userURL)
            st.session_state.articles_list = dynamicWebScraping.scrape_articles(driver)
            delayed_driver_quit(delay=8)
            st.session_state.papers = [article['title'] for article in st.session_state.articles_list]
            st.success("Papers fetched successfully!")

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
                    publication_URL = paper_details["Publication URL"]
                    summary = generate_summary(paper_details.get("Description", "No abstract available."), 4)
                    st.session_state.generated_summary = summary
                    st.markdown("### Summary:")
                    st.write(summary)
                    st.markdown(f"<a href='{publication_URL}' style='text-decoration:none;color:blue;'>Visit Journal</a>", unsafe_allow_html=True)
                    st.write("##### Authors: ", paper_details["Authors"])
                    st.write("Publication Date: ", paper_details.get("Publication date", "Not Available"))
                    st.write("Total citations: ", paper_details.get("Total Citations", "Not Available"))
                else:
                    st.error("Could not find citation URL.")

            if "generated_summary" in st.session_state:
                if st.button("Email Me"):
                    st.session_state.ask_email = True

                if st.session_state.ask_email:
                    with st.form("email_form", clear_on_submit=True):
                        recipient_email = st.text_input("Enter your email to receive the summary:")
                        submitted = st.form_submit_button("Email my Summary")
                        if submitted:
                            if recipient_email:
                                load_dotenv()
                                user_config(
                                    SENDER_EMAIL="akash24400221003@tecb.edu.in",
                                    SENDER_PASSWORD=os.getenv("GMAIL_APP_PASSWORD"),
                                    RECEIVER_EMAIL=recipient_email,
                                    EMAIL_SUBJECT="Your Publication Summary from Scholarly",
                                    EMAIL_BODY_TEXT=f"Dear {st.session_state.userInfo['name']},\n Thank you for using Scholarly, world's 1st automated publication summarizer.\n Please find the detailed information in the attached PDF document.",
                                    LONG_STRING=st.session_state.generated_summary
                                )
                                st.success(f"Summary sent to {recipient_email}")
                                st.session_state.ask_email = False
                            else:
                                st.error("Please enter a valid email address.")

            if st.button("View Stat"):
                view_stat(userURL)
    elif userURL:
        st.error("Invalid Google Scholar Profile URL!!!")


if __name__ == "__main__":
    main()
