# Clash Royale AI Assistant

An AI-powered assistant that analyzes Clash Royale gameplay screenshots and provides strategic move recommendations using GPT-4 Vision.

## Overview

This project captures game state from an Android emulator via ADB and uses OpenAI's GPT-4 Vision API to analyze the current board position, elixir count, available cards, and enemy positions. The AI recommends optimal card placement, timing, and strategic decisions.

## Project Structure

```
clash_royale/
├── main.py
├── screenshot.py
├── ai_client.py
├── config.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- Android emulator (BlueStacks, NoxPlayer, or MEmu)
- OpenAI API key with GPT-4 Vision access

### Setup

1. Clone the repository:

```bash
git clone https://github.com/imad-shah/clash-royale-ai.git
cd clash_royale
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your OpenAI API key in `config.py`:

```python
OPENAI_API_KEY = "your-api-key-here"
```

4. Set up and start your Android emulator with Clash Royale installed.

5. Verify ADB connection:

```bash
adb devices
```

## Usage

Run single analysis:

```bash
python main.py
```

Run continuous analysis mode:

```bash
python main.py --continuous
```
