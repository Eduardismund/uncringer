import json
import vertexai
from vertexai.generative_models import GenerativeModel
import os
from google.oauth2 import service_account


class AwkwardnessClassifier:
    
    def __init__(self, project_id: str = "uncringer-472412", service_account_key: str = None):
        self.project_id = project_id
        
        credentials = None
        
        if service_account_key:
            try:
                key_info = json.loads(service_account_key)
                credentials = service_account.Credentials.from_service_account_info(key_info)
            except Exception:
                pass
        
        if not credentials:
            creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if not creds_path:
                creds_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                    'credentials.json'
                )
                if os.path.exists(creds_path):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        if credentials:
            vertexai.init(project=project_id, location="us-central1", credentials=credentials)
        else:
            vertexai.init(project=project_id, location="us-central1")
            
        self.model = GenerativeModel("gemini-2.0-flash-exp")
    
    def classify(self, reactions: dict) -> dict:
        if not reactions or sum(reactions.values()) == 0:
            return {
                "level": 1,
                "label": "Slightly Awkward", 
                "confidence": 0.3,
                "reason": "No reactions to analyze"
            }
        
        prompt = self._build_prompt(reactions)
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text)
            
            if self._validate_result(result):
                return result
            else:
                raise ValueError("Invalid AI response format")
                
        except Exception as e:
            raise Exception(f"AI classification failed: {str(e)}")
    
    def _build_prompt(self, reactions: dict) -> str:
        return f"""
        Analyze these Discord emoji reactions to an audio message and classify the awkwardness level.

        Reactions: {json.dumps(reactions)}

        Classification Scale:
        0 = Cool/Natural (positive reactions, genuinely funny/good)
        1 = Slightly Awkward (mixed reactions, minor awkwardness)
        2 = Awkward (negative reactions, clear discomfort)
        3 = Very Cringe (strong negative reactions, secondhand embarrassment)

        Consider the emotional meaning of each emoji and their quantities.

        Respond ONLY in this JSON format:
        {{
            "level": <0-3>,
            "label": "<Cool/Natural|Slightly Awkward|Awkward|Very Cringe>",
            "confidence": <0.0-1.0>,
            "reason": "<one sentence explanation>"
        }}
        """
    
    def _validate_result(self, result: dict) -> bool:
        required_keys = ['level', 'label', 'confidence', 'reason']
        valid_levels = [0, 1, 2, 3]
        valid_labels = ["Cool/Natural", "Slightly Awkward", "Awkward", "Very Cringe"]
        
        return (
            all(key in result for key in required_keys) and
            result['level'] in valid_levels and
            result['label'] in valid_labels and
            0 <= result['confidence'] <= 1
        )
    
