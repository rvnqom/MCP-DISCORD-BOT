# utils/hate_speech_model.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model and tokenizer once
tokenizer = AutoTokenizer.from_pretrained("Hate-speech-CNERG/bert-base-uncased-hatexplain")
model = AutoModelForSequenceClassification.from_pretrained("Hate-speech-CNERG/bert-base-uncased-hatexplain")

def analyze_hate_speech(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = torch.softmax(outputs.logits, dim=1)[0]
    labels = ['hate', 'offensive', 'normal']
    result = dict(zip(labels, scores.tolist()))
    return result
