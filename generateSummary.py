import nltk
import networkx as nx
import numpy as np
import re
from nltk.cluster.util import cosine_distance
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from autoCompleteSentence import completeSentence

# Return cleaned & processed sentences
def preprocess_sentences(text):
    try:
        stopwords.words('english')
        sentences = sent_tokenize(text)
    except:
        nltk.download('punkt')
        nltk.download('stopwords')
    processed = []
    for sentence in sentences:
        cleaned = re.sub(r'[^a-zA-Z0-9.% ]', ' ', sentence)
        words = cleaned.lower().split()
        if len(words) > 2:
            processed.append(words)
    return processed, sentences

# Return sentence similarity between two sentences. Used Cosine Distance method to measure the similarity.
def sentence_similarity(sent1, sent2, stopwords = None):
    if stopwords is None:
        stopwords=[]
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
    all_words=list(set(sent1+sent2))
    
    vector1 = [0]*len(all_words)
    vector2 = [0]*len(all_words)
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
    return 1-cosine_distance(vector1, vector2)

# Generate similarity matrix
def gen_sim_matrix(sentences, stop_words):
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    for idx1 in range (len(sentences)):
        for idx2 in range (len(sentences)):
            if idx1 == idx2 :
                continue
        similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
    return similarity_matrix

def generate_summary(input_text, top_n = 4):
    if(input_text[len(input_text) - 1] == "…"):
        new_text = input_text.strip()[:-2]
        input_text = completeSentence(new_text)
    stop_words = stopwords.words('english')
    processed, original_sentences = preprocess_sentences(input_text)
    sim_matrix = gen_sim_matrix(processed, stop_words)
    sim_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(sim_graph)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(original_sentences) if i in scores), reverse=True)
    summary = " ".join([s for _, s in ranked_sentences[:top_n]])
    return summary


if __name__ == "__main__":
    input_text = "Diagnosing cardiovascular disease (CVD) is a crucial issue in healthcare and research on machine learning. Machine-learning techniques can predict risk at an early stage of CVD based on the features of regular lifestyles and results of a few medical tests. The Framingham Heart Study dataset has 15.2% of patients with CVD, which increases the likelihood of classifying CVD patients as healthy. We create approximately equal instances of each class by over-sampling. We evaluate: (i) no over-sampling, (ii) random over-sampling of the training dataset, and (iii) over-sampling before splitting the dataset. We apply 50–50%, 66–34%, and 80–20% train-test splits and 10-fold cross-validation. We compare logistic regression (LR), Naive-Bayes (NB), support vector machine (SVM), decision tree (DT), and random forest (RF) classifiers. The comparison based on accuracy, sensitivity, specificity, area under …"
    print("\nSummary\n", generate_summary(input_text, 4))
