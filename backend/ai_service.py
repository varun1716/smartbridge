import os
import re
import json
import requests
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Global config
AI_PROVIDER = os.getenv("AI_PROVIDER", "fallback").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

class AIService:
    @staticmethod
    def extract_themes_and_generate_starters(event_description: str, interests: List[str]) -> Tuple[List[str], List[str]]:
        """
        Extracts key themes from the event description and generates 2-3 tailored conversation starters.
        Dynamically chooses the AI provider based on configuration and availability.
        """
        provider = AI_PROVIDER
        
        # If Gemini key is provided, prefer Gemini
        if GEMINI_API_KEY and provider == "fallback":
            provider = "gemini"
            
        print(f"Using AI provider: {provider}")
        
        if provider == "gemini":
            try:
                return AIService._run_gemini(event_description, interests)
            except Exception as e:
                print(f"Gemini API failed ({e}), falling back...")
                
        if provider == "huggingface":
            try:
                return AIService._run_huggingface(event_description, interests)
            except Exception as e:
                print(f"Hugging Face Inference API failed ({e}), falling back...")
                
        if provider == "local":
            try:
                return AIService._run_local_transformers(event_description, interests)
            except Exception as e:
                print(f"Local transformers failed ({e}), falling back...")
                
        # Default fallback (Rule-based heuristic)
        return AIService._run_rule_based(event_description, interests)

    @staticmethod
    def _run_rule_based(event_description: str, interests: List[str]) -> Tuple[List[str], List[str]]:
        """
        A robust heuristic backup that extracts themes using keyword matching
        and creates high-quality template-based conversation starters.
        """
        # 1. Extract Themes
        common_themes = [
            "AI", "Artificial Intelligence", "Machine Learning", "Sustainability", "Climate Change", 
            "Urban Planning", "Blockchain", "Healthcare", "Medicine", "Fintech", "Finance", 
            "Education", "EdTech", "E-commerce", "Cloud Computing", "Cybersecurity", "SaaS",
            "Data Science", "Renewable Energy", "Web Development", "Software Engineering", 
            "IoT", "Marketing", "Ventures", "Startups"
        ]
        
        extracted = []
        text_to_scan = (event_description + " " + " ".join(interests)).lower()
        
        for theme in common_themes:
            # Match word boundary to avoid partial matches
            if re.search(r'\b' + re.escape(theme.lower()) + r'\b', text_to_scan):
                # Map some names to standard short themes
                std_theme = theme
                if theme in ["Artificial Intelligence", "Machine Learning"]:
                    std_theme = "AI"
                elif theme in ["Medicine"]:
                    std_theme = "Healthcare"
                if std_theme not in extracted:
                    extracted.append(std_theme)
                    
        # Fallback if no matching standard theme is found
        if not extracted:
            # Try to grab the first word or interest
            if interests:
                extracted = [interests[0].capitalize()]
            else:
                extracted = ["Innovation"]
                
        # Limit themes to top 3
        extracted_themes = extracted[:3]
        
        # 2. Generate Starters
        starters = []
        primary_interest = interests[0] if interests else "industry trends"
        secondary_interest = interests[1] if len(interests) > 1 else primary_interest
        primary_theme = extracted_themes[0]
        
        # Starter 1: Context-aware standard starter
        starters.append(
            f"Hi! I noticed the event focus on '{event_description.strip('.')}'. With your interest in {primary_interest}, "
            f"how do you see the theme of {primary_theme} transforming projects in that space?"
        )
        
        # Starter 2: Thought provoking question
        starters.append(
            f"Hello! I saw you are passionate about {primary_interest}. I've been thinking about how {primary_theme} "
            f"is shaping {secondary_interest} lately. What's your perspective on the biggest challenge we face there?"
        )
        
        # Starter 3: Action-oriented connection starter
        starters.append(
            f"Hi there, great to meet you! Given your background in {primary_interest}, what do you think is the "
            f"most promising application of {primary_theme} mentioned in today's talks?"
        )
        
        return extracted_themes, starters

    @staticmethod
    def _run_gemini(event_description: str, interests: List[str]) -> Tuple[List[str], List[str]]:
        """
        Uses Google Gemini to extract themes and generate conversation starters.
        """
        import google.generativeai as genai
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are an expert networking assistant.
        Given the event description: "{event_description}"
        And the user's interests: {interests}

        Perform the following tasks:
        1. Extract 2-3 key thematic keywords or phrases from the event description (e.g. AI, Sustainability).
        2. Generate exactly 3 highly personalized, engaging, and professional conversation starters that the user can use at this event. The starters must connect their interests with the event themes.

        Provide the output in JSON format with exactly the following structure:
        {{
            "themes": ["theme1", "theme2"],
            "starters": [
                "Starter 1 text...",
                "Starter 2 text...",
                "Starter 3 text..."
            ]
        }}
        Do not return any markdown formatting outside of the JSON block. Return ONLY the JSON object.
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Strip markdown json blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        return data["themes"], data["starters"]

    @staticmethod
    def _run_huggingface(event_description: str, interests: List[str]) -> Tuple[List[str], List[str]]:
        """
        Queries Hugging Face's Serverless Inference API for theme extraction (DistilBERT)
        and prompt generation (GPT-2).
        """
        headers = {}
        if HF_API_TOKEN:
            headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
            
        # 1. Extract themes using a Zero-Shot Classification model (based on DistilBERT/BART)
        # We can query 'typeform/distilbert-base-uncased-mnli'
        theme_api_url = "https://api-inference.huggingface.co/models/typeform/distilbert-base-uncased-mnli"
        
        candidate_labels = [
            "Artificial Intelligence", "Sustainability", "Blockchain", "Healthcare", 
            "Fintech", "Climate Change", "Urban Planning", "Education", "SaaS"
        ]
        
        payload = {
            "inputs": f"Event: {event_description}. Interests: {', '.join(interests)}",
            "parameters": {"candidate_labels": candidate_labels}
        }
        
        extracted_themes = []
        try:
            response = requests.post(theme_api_url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                # Get labels with high score (e.g. > 0.15)
                labels = result.get("labels", [])
                scores = result.get("scores", [])
                for label, score in zip(labels, scores):
                    if score > 0.18:
                        # Normalize label name
                        std_label = "AI" if label == "Artificial Intelligence" else label
                        extracted_themes.append(std_label)
        except Exception as e:
            print(f"HF Theme extraction query error: {e}")
            
        # Fallback theme if classification failed
        if not extracted_themes:
            extracted_themes = [interests[0].capitalize()] if interests else ["Networking"]
        extracted_themes = extracted_themes[:3]
        
        # 2. Generate starters using GPT-2
        gpt2_api_url = "https://api-inference.huggingface.co/models/gpt2"
        
        starters = []
        primary_interest = interests[0] if interests else "industry trends"
        primary_theme = extracted_themes[0]
        
        # Since GPT-2 is a text completer, we prompt it and then clean/format the response.
        # We query GPT-2 three times with different prefixes to generate 3 starters.
        prompts = [
            f"A professional conversation starter at a '{event_description}' conference combining '{primary_theme}' and '{primary_interest}': \"Hello, ",
            f"An insightful networking question about '{primary_theme}' and '{primary_interest}': \"Hi, I was thinking about ",
            f"A friendly starter connecting '{primary_theme}' to '{primary_interest}': \"Hey there! As someone interested in "
        ]
        
        for idx, prompt_text in enumerate(prompts):
            try:
                payload = {
                    "inputs": prompt_text,
                    "parameters": {
                        "max_new_tokens": 40,
                        "temperature": 0.7,
                        "return_full_text": True
                    }
                }
                res = requests.post(gpt2_api_url, json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    text_out = res.json()[0]["generated_text"]
                    # Extract the generated text and clean up quotes/sentences
                    cleaned = text_out.replace(prompt_text, "").strip()
                    # Keep only until first sentence end or complete phrase
                    cleaned = re.split(r'[.!?]\s*', cleaned)[0]
                    
                    # Reconstruct starter
                    prefix = "Hello, " if idx == 0 else ("Hi, I was thinking about " if idx == 1 else "Hey there! As someone interested in ")
                    starter = f"{prefix}{cleaned}."
                    
                    # Basic sanity check (ensure it generated something useful)
                    if len(cleaned) > 10 and not cleaned.startswith("...") and "GPT" not in cleaned:
                        starters.append(starter)
            except Exception as e:
                print(f"HF GPT-2 generation query error: {e}")
                
        # If GPT-2 generation fails or is too short, supplement with heuristic starters
        if len(starters) < 3:
            _, backup_starters = AIService._run_rule_based(event_description, interests)
            for b_starter in backup_starters:
                if len(starters) < 3 and b_starter not in starters:
                    starters.append(b_starter)
                    
        return extracted_themes, starters

    @staticmethod
    def _run_local_transformers(event_description: str, interests: List[str]) -> Tuple[List[str], List[str]]:
        """
        Loads models locally using HuggingFace's transformers library.
        Fails dynamically if torch or transformers are not installed.
        """
        from transformers import pipeline
        
        # 1. Zero shot classification with DistilBERT
        classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
        candidate_labels = [
            "AI", "Sustainability", "Blockchain", "Healthcare", 
            "Fintech", "Climate Change", "Urban Planning", "Education", "SaaS"
        ]
        
        res = classifier(
            f"Event: {event_description}. Interests: {', '.join(interests)}",
            candidate_labels=candidate_labels
        )
        
        extracted_themes = []
        for label, score in zip(res["labels"], res["scores"]):
            if score > 0.18:
                extracted_themes.append(label)
                
        if not extracted_themes:
            extracted_themes = [interests[0].capitalize()] if interests else ["Networking"]
        extracted_themes = extracted_themes[:3]
        
        # 2. Text generation with GPT-2
        generator = pipeline("text-generation", model="gpt2")
        
        starters = []
        primary_interest = interests[0] if interests else "industry trends"
        primary_theme = extracted_themes[0]
        
        prompt_prefix = f"A professional conversation starter at a '{event_description}' conference combining '{primary_theme}' and '{primary_interest}': \""
        
        try:
            outputs = generator(
                prompt_prefix,
                max_length=60,
                num_return_sequences=3,
                pad_token_id=50256
            )
            for out in outputs:
                gen_text = out["generated_text"]
                cleaned = gen_text.replace(prompt_prefix, "").strip()
                # Keep only until first sentence end or complete phrase
                sentence_match = re.split(r'[.!?]\s*', cleaned)
                if sentence_match:
                    cleaned_sentence = sentence_match[0]
                else:
                    cleaned_sentence = cleaned
                
                # Format starter
                starter = f"Hi! {cleaned_sentence}."
                if len(cleaned_sentence) > 10 and starter not in starters:
                    starters.append(starter)
        except Exception as e:
            print(f"Local GPT-2 generation error: {e}")
            
        if len(starters) < 3:
            _, backup_starters = AIService._run_rule_based(event_description, interests)
            for b_starter in backup_starters:
                if len(starters) < 3 and b_starter not in starters:
                    starters.append(b_starter)
                    
        return extracted_themes, starters
