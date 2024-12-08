from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from utils.device import get_device
import logging

class TransformersModel:
    def __init__(self, model_name: str):
        self.device = get_device()
        logging.info("Loading model and tokenizer...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        logging.info("Tokenizer loaded")
        
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)
        logging.info("Model loaded")
    
    def generate_response(self, text: str, max_length=32, num_beams=4):
        inputs = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
        outputs = self.model.generate(inputs, max_length=max_length, num_beams=num_beams, early_stopping=True)
        response = self.tokenizer.decode(outputs[0].to("cpu"))
        return response.replace("<pad>", "").replace("<s>", "").replace("</s>", "").strip()
