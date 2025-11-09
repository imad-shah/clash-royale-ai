import json
from openai import OpenAI
import config


class ClashRoyaleAI:
    def __init__(self):
        if not config.validate_config():
            raise Exception("Invalid configuration! Check config.py")

        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.GPT_MODEL
        print(f"AI Client initialized (model: {self.model})")

    def analyze_game_state(self, base64_image):
        """
        Analyze Clash Royale screenshot and recommend best move

        Args:
            base64_image (str): Base64-encoded screenshot

        Returns:
            dict: Parsed JSON response with recommendation
        """
        try:
            prompt = self._create_analysis_prompt()
            print("Analyzing screenshot with GPT-4 Vision...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  
                                }
                            }
                        ]
                    }
                ],
                max_tokens=config.MAX_TOKENS,
                temperature=config.ANALYSIS_TEMPERATURE
            )

            ai_response = response.choices[0].message.content
            print(f"AI analysis complete")

            try:
                parsed_response = json.loads(ai_response)
                return parsed_response
            except json.JSONDecodeError:
                print("Response not in JSON format, returning raw text")
                return {
                    "raw_response": ai_response,
                    "recommended_card": "Unknown",
                    "reasoning": ai_response
                }

        except Exception as e:
            print(f"AI analysis failed: {e}")
            raise

    def _create_analysis_prompt(self):
        """
        Create the prompt for analyzing Clash Royale game state
        """
        prompt = """You are an expert Clash Royale AI assistant. Analyze this game screenshot and recommend the optimal play.

**What to analyze:**
1. **Elixir count** - How much elixir is available?
2. **Cards in hand** - What cards are available to play?
3. **Enemy troops** - What troops/buildings are on the arena?
4. **Tower status** - King tower and princess tower health
5. **Arena positioning** - Where are troops located?
6. **Optimal strategy** - Should we attack, defend, or wait?

**Response format (JSON):**
```json
{
    "elixir": <current elixir count>,
    "cards_in_hand": ["card1", "card2", "card3", "card4"],
    "recommended_card": "<card to play>",
    "placement": "<where to place it (e.g., 'left bridge', 'center', 'behind king tower')>",
    "reasoning": "<why this move is optimal>",
    "game_state": "<brief description of current situation>",
    "strategy": "<attack/defend/wait>",
    "confidence": <0-100>
}
```

**Important:**
- If elixir is low, recommend waiting
- Consider elixir cost vs available elixir
- Prioritize defense if enemy is attacking
- Look for counter-push opportunities
- Consider card cycle and upcoming cards

Analyze the screenshot and respond ONLY with valid JSON matching the format above."""

        return prompt

    def get_simple_recommendation(self, base64_image):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this Clash Royale screenshot and suggest the best move in 2-3 sentences."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Analysis failed: {e}")
            raise

if __name__ == "__main__":
    print("=" * 50)
    print("AI CLIENT TEST")
    print("=" * 50)


    import os
    import base64

    sample_file = "test_screenshot.png"

    if not os.path.exists(sample_file):
        print(f"\nNo sample screenshot found ({sample_file})")
        print("Options:")
        print("1. Wait for Person A to create test_screenshot.png")
        print("2. Download a Clash Royale screenshot and save as test_screenshot.png")
        print("3. Skip visual test and just test API connection")
        print("\nTesting API connection only...")

        try:
            ai = ClashRoyaleAI()
            print("API client initialized successfully!")
            print("\nReady for integration once screenshots are available.")
        except Exception as e:
            print(f"Initialization failed: {e}")

    else:
        print(f"\nFound sample screenshot: {sample_file}")

        # Load and encode image
        with open(sample_file, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Test AI analysis
        ai = ClashRoyaleAI()

        print("\nTest 1: Simple recommendation...")
        simple_rec = ai.get_simple_recommendation(image_data)
        print(f"Recommendation: {simple_rec}")

        print("\nTest 2: Full analysis...")
        analysis = ai.analyze_game_state(image_data)
        print("\nAnalysis Result:")
        print(json.dumps(analysis, indent=2))

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Refine the prompt if needed")
        print("2. Commit and push your changes")
