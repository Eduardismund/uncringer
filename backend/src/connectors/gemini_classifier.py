import json
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
from typing import Dict, Optional
from config import ConnectorConfig


class GeminiClassifier:

    def __init__(self, project_id: str = None, credentials_json: str = None):
        self.project_id = project_id or ConnectorConfig.PROJECT_ID
        self._setup_client(credentials_json)
        
    def _setup_client(self, credentials_json: Optional[str] = None):
        credentials = None
        
        if credentials_json:
            try:
                key_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(key_info)
            except json.JSONDecodeError:
                pass
        
        if credentials:
            vertexai.init(project=self.project_id, location="us-central1", credentials=credentials)
        else:
            vertexai.init(project=self.project_id, location="us-central1")
            
        self.model = GenerativeModel("gemini-2.0-flash-exp")
    
    def classify_reactions(self, reactions: Dict[str, int]) -> Dict:
        if not reactions or sum(reactions.values()) == 0:
            return {
                "is_cringe": True,
                "confidence": 0.7,
                "reason": "No reactions suggests awkward silence"
            }
        
        prompt = self._build_prompt(reactions)
        
        try:
            response = self.model.generate_content(prompt)
            response_text = self._clean_response(response.text)
            result = json.loads(response_text)
            
            if self._validate_result(result):
                return result
            else:
                raise ValueError("Invalid AI response format")
                
        except Exception as e:
            raise Exception(f"AI classification failed: {str(e)}")
    
    def _build_prompt(self, reactions: Dict[str, int]) -> str:
        return f"""
        Analyze these Discord emoji reactions to an audio message and classify if it's cringe or not.

        Reactions: {json.dumps(reactions)}

        Binary Classification:
        - NOT CRINGE (0): Positive reactions, genuinely funny, cool, normal conversation
        - CRINGE (1): Awkward reactions, discomfort, secondhand embarrassment, negative feedback

        Consider the emotional meaning of each emoji and their quantities.
        Look for cringe indicators: 😬 🫣 😐 😑 💀 🤐 😶 or very few/no reactions.
        Look for positive indicators: 😂 🔥 ❤️ 👏 💯 or many enthusiastic reactions.

        Respond ONLY in this JSON format:
        {{
            "is_cringe": <true or false>,
            "confidence": <0.0-1.0>,
            "reason": "<one sentence explanation>"
        }}
        """
    
    def _clean_response(self, response_text: str) -> str:
        """Clean up Gemini response text"""
        response_text = response_text.strip()
        
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        elif response_text.startswith('```'):
            response_text = response_text[3:]
            
        if response_text.endswith('```'):
            response_text = response_text[:-3]
            
        return response_text.strip()
    
    def _validate_result(self, result: Dict) -> bool:
        """Validate classification result format"""
        required_keys = ['is_cringe', 'confidence', 'reason']
        
        return (
            all(key in result for key in required_keys) and
            isinstance(result['is_cringe'], bool) and
            isinstance(result['confidence'], (int, float)) and
            0 <= result['confidence'] <= 1 and
            isinstance(result['reason'], str)
        )