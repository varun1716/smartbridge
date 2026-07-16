import requests
import json
import time

BACKEND_URL = "http://127.0.0.1:8000"

def test_flow():
    print("=" * 60)
    print("Verifying Application Integration Flows...")
    print("=" * 60)
    
    # 1. Health check
    try:
        res = requests.get(f"{BACKEND_URL}/")
        print(f"[Health Check] Status: {res.status_code}, Response: {res.json()}")
        assert res.status_code == 200
    except Exception as e:
        print(f"[Health Check] Failed: {e}")
        return False
        
    # 2. Generate starters
    payload = {
        "event_description": "AI for Sustainable Cities Panel Discussion",
        "interests": ["climate change", "urban planning"]
    }
    try:
        res = requests.post(f"{BACKEND_URL}/api/generate-starters", json=payload)
        data = res.json()
        print(f"[Generate Starters] Status: {res.status_code}")
        print(f"  Extracted Themes: {data.get('extracted_themes')}")
        print(f"  First Starter: {data.get('conversation_starters')[0] if data.get('conversation_starters') else None}")
        assert res.status_code == 201
        interaction_id = data["id"]
    except Exception as e:
        print(f"[Generate Starters] Failed: {e}")
        return False
        
    # 3. Post feedback
    try:
        feedback_payload = {
            "interaction_id": interaction_id,
            "feedback": "thumbs_up"
        }
        res = requests.post(f"{BACKEND_URL}/api/feedback", json=feedback_payload)
        print(f"[Post Feedback] Status: {res.status_code}, Response: {res.json()}")
        assert res.status_code == 200
    except Exception as e:
        print(f"[Post Feedback] Failed: {e}")
        return False
        
    # 4. Fact check
    try:
        res = requests.get(f"{BACKEND_URL}/api/fact-check", params={"query": "blockchain in healthcare"})
        data = res.json()
        print(f"[Fact Check] Status: {res.status_code}")
        print(f"  Topic Found: {data.get('topic')}")
        print(f"  Summary: {data.get('summary')[:100]}...")
        assert res.status_code == 200
    except Exception as e:
        print(f"[Fact Check] Failed: {e}")
        return False
        
    # 5. History and feedback validation
    try:
        res = requests.get(f"{BACKEND_URL}/api/history")
        history = res.json()
        print(f"[Get History] Status: {res.status_code}, Total records: {len(history)}")
        # Verify our interaction feedback is thumbs_up
        matched = [h for h in history if h["id"] == interaction_id]
        print(f"  Verified Saved Feedback for ID {interaction_id}: {matched[0]['feedback'] if matched else None}")
        assert len(matched) == 1
        assert matched[0]["feedback"] == "thumbs_up"
    except Exception as e:
        print(f"[Get History] Failed: {e}")
        return False
        
    print("=" * 60)
    print("All integration flows verified successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    # Give server a second if needed
    time.sleep(1)
    test_flow()
