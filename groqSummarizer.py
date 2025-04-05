import os
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate


load_dotenv()
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="deepseek-r1-distill-llama-70b")

def generate_summary_response(paperTitle, abstract, publicationLink):
    summary_prompt = PromptTemplate(
        input_variables=["paperTitle", "abstract", "publicationLink"],
        template=(
            "Summarize the following research paper within 60 words or less, titled as '{paperTitle}', "
            "by using its abstract. Highlight objectives, key features, methods used, and results obtained."
            "No preamble. Focus on numbers, percentages etc. If possible, use corresponding publication journal link for better summary: {publicationLink}"
            "Abstract:\n\n{abstract}"
        ),
    )
    if abstract.strip():
        response = llm.invoke(summary_prompt.format(paperTitle=paperTitle, abstract=abstract, publicationLink=publicationLink), reasoning_format="parsed")
        return response.content
    else:
        errMsg = "Error: Unable to generate summary"
        return errMsg



if __name__ == "__main__":
    
    paperTitle = "An Improved Random Forest Model for Detecting Heart Disease"
    publicationLink = "https://www.taylorfrancis.com/chapters/edit/10.1201/9781003356189-10/improved-random-forest-model-detecting-heart-disease-avijit-kumar-chaudhuri-sulekha-das-arkadip-ray"
    
    abstract = """Diagnosing cardiovascular disease (CVD) is a crucial issue in healthcare and research on machine learning. Machine-learning techniques can predict risk at an early stage of CVD based on the features of regular lifestyles and results of a few medical tests. The Framingham Heart Study dataset has 15.2% of patients with CVD, which increases the likelihood of classifying CVD patients as healthy. We create approximately equal instances of each class by over-sampling. We evaluate: (i) no over-sampling, (ii) random over-sampling of the training dataset, and (iii) over-sampling before splitting the dataset. We apply 50–50%, 66–34%, and 80–20% train-test splits and 10-fold cross-validation. We compare logistic regression (LR), Naive-Bayes (NB), support vector machine (SVM), decision tree (DT), and random forest (RF) classifiers. The comparison based on accuracy, sensitivity, specificity, area under …"""
    
    summary_prompt = PromptTemplate(
        input_variables=["paperTitle", "abstract", "publicationLink"],
        template=(
            "Summarize the following research paper within 60 words or less, titled as '{paperTitle}', "
            "by using its abstract. Highlight objectives, key features, methods used, and main findings."
            "No preamble. If possible, use corresponding publication journal link for better summary: {publicationLink}"
            "Abstract:\n\n{abstract}"
        ),
    )
    response = llm.invoke(summary_prompt.format(paperTitle=paperTitle, abstract=abstract, publicationLink=publicationLink), reasoning_format="parsed")
    print("Summary\n", response.content)

