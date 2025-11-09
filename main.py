import sys
import json
from screenshot import ScreenshotCapture
from ai_client import ClashRoyaleAI
import config


class ClashRoyaleAssistant:
    def __init__(self):
        """Initialize screenshot capture and AI client"""
        print("=" * 60)
        print("Clash Royale AI Assistant")
        print("=" * 60)

        print("\n1. Initializing screenshot capture...")
        self.screenshot = ScreenshotCapture(emulator_port=config.EMULATOR_PORT)

        print("\n2. Initializing AI client...")
        self.ai = ClashRoyaleAI()

        print("\nAssistant ready!")

    def analyze_current_game(self):
        try:
            print("\n" + "-" * 60)
            print("Connecting to emulator...")
            if not self.screenshot.connect():
                raise Exception("Failed to connect to emulator")

            print("\nCapturing screenshot...")
            base64_image = self.screenshot.capture_screenshot()

            print("\nAnalyzing game state with GPT-4 Vision...")
            analysis = self.ai.analyze_game_state(base64_image)

            self._display_recommendation(analysis)

            return analysis

        except Exception as e:
            print(f"\nError: {e}")
            raise

    def _display_recommendation(self, analysis):
        print("\n" + "=" * 60)
        print("AI RECOMMENDATION")
        print("=" * 60)

        if isinstance(analysis, dict):
            if "raw_response" in analysis:
                print(analysis["raw_response"])
            else:
                # JSON response
                print(f"\nElixir: {analysis.get('elixir', 'Unknown')}")
                print(f"\nCards in hand: {', '.join(analysis.get('cards_in_hand', ['Unknown']))}")
                print(f"\nRECOMMENDED MOVE:")
                print(f"   Card: {analysis.get('recommended_card', 'Unknown')}")
                print(f"   Placement: {analysis.get('placement', 'Unknown')}")
                print(f"   Strategy: {analysis.get('strategy', 'Unknown')}")
                print(f"\nReasoning:")
                print(f"   {analysis.get('reasoning', 'No reasoning provided')}")
                print(f"\nGame State:")
                print(f"   {analysis.get('game_state', 'Unknown')}")
                print(f"\nConfidence: {analysis.get('confidence', 0)}%")
        else:
            print(analysis)

        print("=" * 60)

    def run_continuous(self):
        print("\nStarting continuous mode...")
        print("Press Ctrl+C to stop")

        try:
            while True:
                analysis = self.analyze_current_game()
                input("\nPress Enter to analyze next position (or Ctrl+C to quit)...")

        except KeyboardInterrupt:
            print("\n\nShutting down assistant...")
            sys.exit(0)


def main():
    mode = "single"  

    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            mode = "continuous"
        elif sys.argv[1] == "--help":
            print("Usage: python main.py [--continuous]")
            print("\nModes:")
            print("  (default)      Single analysis, then exit")
            print("  --continuous   Continuous analysis loop")
            sys.exit(0)

    try:
        assistant = ClashRoyaleAssistant()

        if mode == "continuous":
            assistant.run_continuous()
        else:

            assistant.analyze_current_game()
            print("\n✓ Analysis complete!")
            print("\nRun with --continuous for continuous mode")

    except Exception as e:
        print(f"\nFatal error: {e}")
        print("\nTroubleshooting:")
        print("1. Is your emulator running?")
        print("2. Is ADB enabled?")
        print("3. Is your OpenAI API key set in config.py?")
        print("4. Try: python screenshot.py  # Test screenshot")
        print("5. Try: python ai_client.py   # Test AI")
        sys.exit(1)


if __name__ == "__main__":
    main()
