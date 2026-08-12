# main.py
import os
from datetime import datetime
from google import genai

def generate_stoic_reflection():
  # Fetch API from GitHub secrets
  api_key = os.environ.get("LLM_API_KEY")
  if not api_key:
    print("Error: LLM_API_KEY environment variable not found.")
    return
  # Initialize Gemini client
  client = genai.Client(api_key=api_key)
  # Craft prompt
  prompt = (
     "Act as a modern Stoic philosopher. Provide a brief daily Stoic quote "
     "from Marcus Aurelius, Seneca, or Epictetus. Follow it with a 3-sentence "
     "practical explanation and one actionable exercise for today. "
     "Keep the tone grounded and clear."
  )
  
  # Request a response
  response = client.models.generate_content(
    model = 'gemini-3.6-flash',
    contents = prompt,
  )
  reflection_text = response.text
  
  # set the date of the daily reflection
  current_date = datetime.now().strftime("%Y-%m-%d")
  
  # append the result to a markdown file that serves as a log of all reflections
  with open("daily_reflections_log.md", "a", encoding = "utf-8") as file:
    file.write(f"\n\n## Daily Reflection for {current_date}\n")
    file.write(reflection_text)
  # prepare a readme
  readme_content = f"""# 🏛️ Daily Stoic Bot

Welcome! This repository uses AI and GitHub Actions to generate a fresh, daily interpretation of Stoic philosophy every morning.

## 🌟 Today's Stoic Reflection ({current_date})

{reflection_text}

---
Please consider sponsoring me as a sign of support.

*Looking for older entries? Check out the full **[Daily Reflections Archive](./daily_reflections_log.md)**.*
"""
  # save the text to a temp file that can pass into email
  with open("today_reflection.txt", "w", encoding = "utf-8") as file:
    file.write(reflection_text)
  
  # save the daily log into the Readme for the repo and print that it's complete
  with open("README.md", "w", encoding="utf-8") as file:
      file.write(readme_content)
  
  print("Successfully updated README.md and daily_reflections_log.md")

if __name__ == "__main__":
  generate_stoic_reflection()
