"""
AI-Powered Discord Reaction Analysis
Uses Vertex AI to analyze emoji reactions and determine cringe levels
"""

import vertexai
from vertexai.generative_models import GenerativeModel
import json
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class AIReactionAnalyzer:
    def __init__(self):
        creds_path = os.path.join(os.path.dirname(__file__), "../../../credentials.json")
        if os.path.exists(creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        
        vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location="us-central1")
        self.model = GenerativeModel("gemini-2.0-flash-001")
    
    async def analyze_reactions(self, reactions: Dict[str, int], context: str = "") -> Dict:
        
        reactions_text = ", ".join([f"{emoji} ({count})" for emoji, count in reactions.items()])
        
        prompt = f"""
        Analyze these Discord message reactions to determine the cringe level:
        
        Reactions: {reactions_text}
        Context: {context}
        
        Consider:
        - What emotions do these emojis represent?
        - Do they indicate awkwardness, embarrassment, or social discomfort?
        - How many people reacted and with what intensity?
        - Are these reactions positive, negative, or neutral?
        
        Provide a JSON response with:
        {{
            "cringe_score": <float 0-10>,
            "confidence": <float 0-1>,
            "primary_emotion": "<emotion>",
            "reasoning": "<explanation>",
            "reaction_categories": {{
                "cringe": <count>,
                "positive": <count>,
                "neutral": <count>
            }}
        }}
        
        Scale:
        0-2: Very positive/funny
        3-4: Mildly awkward but okay
        5-6: Moderately cringe
        7-8: Very cringe/awkward
        9-10: Extremely cringe/secondhand embarrassment
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            result = json.loads(json_text)
            return result
            
        except Exception as e:
            # Log the actual response for debugging
            print(f"AI Response: {response.text if 'response' in locals() else 'No response'}")
            print(f"Error: {str(e)}")
            
            # Fallback if AI fails
            return {
                "cringe_score": 5.0,
                "confidence": 0.3,
                "primary_emotion": "unknown",
                "reasoning": f"AI analysis failed: {str(e)}",
                "reaction_categories": {"cringe": 0, "positive": 0, "neutral": len(reactions)}
            }
    
    async def create_training_sample(self, audio_data: Dict, reactions: Dict[str, int]) -> Dict:
        """Create AI-analyzed training sample"""
        
        context = f"Audio duration: {audio_data.get('duration', 0)}s"
        if audio_data.get('transcript'):
            context += f", Preview: {audio_data['transcript'][:100]}..."
        
        analysis = await self.analyze_reactions(reactions, context)
        
        return {
            "audio_id": audio_data.get("id"),
            "transcript": audio_data.get("transcript", ""),
            "reactions": reactions,
            "ai_analysis": analysis,
            "cringe_score": analysis["cringe_score"],
            "confidence": analysis["confidence"],
            "source": "ai_reaction_analysis"
        }