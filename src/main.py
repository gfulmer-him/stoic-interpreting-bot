# main.py
import os
from datetime import datetime
from google import genai

def fetch_and_check_quote(recent_quotation_file = "recently_quoted.txt"):
    if not os.path.exists(recent_quotation_file):
        open(recent_quotation_file, "w").close()
    with open(recent_quotation_file, "r") as f:
        recent_quotes = [line.strip() for line in f.readlines() if line.strip()]
    # Fetch API from GitHub secrets
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        print("Error: LLM_API_KEY environment variable not found.")
        return
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    # Craft prompt that requests a quotation, but it must be different from the previous quotations.
    history_string = "\n".join(recent_quotes) if recent_quotes else "None"
    prompt = (
        f"Find a brief daily Stoic quote from Marcus Aurelius, Seneca, Epictetus, Massimo Pigliuicci, or Wiliam B. Irvine. "
        f"CRITICAL: It must NOT be identical or highly similar to any quote in this list:\n"
        f"{history_string}\n\n"
        f"Output Requirements:\n"
        f"1. You must return everything on a single, continuous line.\n"
        f"2. Use this exact format: \"[Quote text here]\" — [Author Name]\n"
        f"3. Do not include any line breaks, extra text, or conversational intros."
    )
    # Request a quotation
    test_quotation = client.models.generate_content(
        model = 'gemini-3.6-flash',
        contents = prompt,
        )
    # Strip whitespace, replace actual newlines/carriage returns with a single space
    quotation_text = test_quotation.text.strip().replace("\n", " ").replace("\r", "")
    # Clean up any accidental double spaces caused by the newline removal
    quotation_text = " ".join(quotation_text.split())
    recent_quotes.append(quotation_text)
    if len(recent_quotes) > 10:
        recent_quotes.pop(0)  # Keep only the last 10 entries
    with open(recent_quotation_file, "w") as f:
        for q in recent_quotes:
            f.write(f"{q}\n")    
    return quotation_text        
      
def generate_stoic_reflection(stoic_quotation):
  # Fetch API from GitHub secrets
  api_key = os.environ.get("LLM_API_KEY")
  if not api_key:
    print("Error: LLM_API_KEY environment variable not found.")
    return
  # Initialize Gemini client
  client = genai.Client(api_key=api_key)
  # Craft prompt
  prompt = (
     f"Act as a modern Stoic philosopher who wants to share an interpretion of the following quotation: "
     f"{stoic_quotation} with a general audience. "
     f"Restate the quotation and, if necessary, add who the author is. Then follow that with a 3-sentence "
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

To receive these daily updates directly in your email inbox, click the Watch button at the top of this repository, select Custom, check Releases, and click Apply!

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
    today_quotation = fetch_and_check_quote()
    generate_stoic_reflection(today_quotation)
