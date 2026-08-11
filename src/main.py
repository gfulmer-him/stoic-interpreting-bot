# main.py
import os
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
  # append the result to a markdown file
  with open("daily_reflections.md", "a", encoding = "utf-8") as file:
    file.write(f"\n\n## Daily Reflection\n")
    file.write(reflection_text)
  print("Successfully updated daily_reflections.md")

if __name__ == "__main__":
  generate_stoic_reflection()
