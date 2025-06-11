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
            do_sample=True,
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
    input_text = "Diagnosing cardiovascular disease (CVD) is a crucial issue in healthcare and research on machine learning. Machine-learning techniques can predict risk at an early stage of CVD based on the features of regular lifestyles and results of a few medical tests. The Framingham Heart Study dataset has 15.2% of patients with CVD, which increases the likelihood of classifying CVD patients as healthy. We create approximately equal instances of each class by over-sampling. We evaluate: (i) no over-sampling, (ii) random over-sampling of the training dataset, and (iii) over-sampling before splitting the dataset. We apply 50–50%, 66–34%, and 80–20% train-test splits and 10-fold cross-validation. We compare logistic regression (LR), Naive-Bayes (NB), support vector machine (SVM), decision tree (DT), and random forest (RF) classifiers. The comparison based on accuracy, sensitivity, specificity, area under"
    print("\nCompleted Abstract\n", completeSentence(input_text))
