from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

def completeSentence(input_text):
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    input_ids = tokenizer.encode(input_text, return_tensors='pt').to(device)
    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_length=len(input_ids[0]) + 40,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            early_stopping=True,
            eos_token_id=tokenizer.eos_token_id,
            temperature=0.7,
            top_k=50,
            top_p=0.9
        )
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    # Handling extra texts
    sentences = generated_text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences and not generated_text.endswith('.'):
        sentences = sentences[:-1]
    finalCleanedSen = '. '.join(sentences) + ('.' if generated_text.endswith('.') and sentences else '')
    return finalCleanedSen.strip() + '.'


if __name__ == "__main__":
    input_text = "World Health Organisation declared breast cancer (BC) as the most frequent suffering among women and accounted for 15 percent of all cancer deaths. Its accurate prediction is of utmost significance as it not only prevents deaths but also stops mistreatments. The conventional way of diagnosis includes the estimation of the tumor size as a sign of plausible cancer. Machine learning (ML) techniques have shown the effectiveness of predicting disease. However, the ML methods have been method centric rather than being dataset centric. In this paper, the authors introduce a dataset centric approach (DCA) deploying a genetic algorithm (GA) method to identify the features and a learning ensemble classifier algorithm to predict using the right features. Adaboost is such an approach that trains the model assigning weights to individual records rather than experimenting on the splitting of datasets alone and perform hyper-parameter optimization. The authors simulate the results by varying base classifiers ie, using logistic regression (LR), decision tree (DT), support vector machine (SVM), naive bayes (NB), random forest (RF), and 10-fold crossvalidations with a different split of the dataset as training and testing. The proposed DCA model with RF and 10-fold cross-validations demonstrated its potential with almost 100% performance in the classification results that no research could suggest so far. The DCA satisfies the underlying principles of data mining: the principle of parsimony, the principle of inclusion, the principle of discrimination, and the principle of optimality. This DCA is a democratic and unbiased ensemble approach as it allows all features"
    print(completeSentence(input_text))