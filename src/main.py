# main.py
import os
import time
from datetime import datetime
from google import genai
from google.genai.errors import ServerError, APIError

def fetch_and_check_quote() -> str:
    if not os.path.exists("recently_quoted.txt"):
        open("recently_quoted.txt", "w").close()
    with open("recently_quoted.txt", "r", encoding = "utf-8") as f:
        recent_quotes = [line.strip() for line in f.readlines() if line.strip()]
    # Fetch API from GitHub secrets
    api_key = os.environ.get("LLM_API_KEY")
    MODEL_ID = 'gemini-3.6-flash'
    MAX_STORED_QUOTES = 21
    MAX_RETRIES = 3
    if not api_key:
        print("Error: LLM_API_KEY environment variable not found.")
        return
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    # Craft prompt that requests a quotation, but it must be different from the previous quotations.
    history_string = "\n".join(recent_quotes) if recent_quotes else "None"
    quote_prompt = (
        f"Find a brief daily Stoic quote from Marcus Aurelius, Seneca, Epictetus, Massimo Pigliuicci, or Wiliam B. Irvine. "
        f"CRITICAL: It must NOT be identical or highly similar to any quote in this list:\n"
        f"{history_string}\n\n"
        f"Output Requirements:\n"
        f"1. You must return everything on a single, continuous line.\n"
        f"2. Use this exact format: \"[Quote text here]\" — [Author Name]\n"
        f"3. Do not include any line breaks, extra text, or conversational intros."
    )
    # Initiate a chat
    chat = client.chats.create(model=MODEL_ID)
    for attempt in range(MAX_RETRIES):
        try:
            # Request a quotation
            quote_response = chat.send_message(quote_prompt)
            # Strip whitespace, replace actual newlines/carriage returns with a single space
            quotation_text = quote_response.text.strip().replace("\n", " ").replace("\r", "")
            # Clean up any accidental double spaces caused by the newline removal
            quotation_text = " ".join(quotation_text.split())
            recent_quotes.append(quotation_text)
            if len(recent_quotes) > MAX_STORED_QUOTES:
                recent_quotes.pop(0)  # Keep only the last 10 entries
            with open("recently_quoted.txt", "w") as f:
                for q in recent_quotes:
                    f.write(f"{q}\n")    
            return quotation_text
        except ServerError as e:
            # check any 500 level error
            if e.code >= 500 and attempt < MAX_RETRIES - 1:
                sleep_time = (attempt + 1) * 5
                print(f"Gemini API 503 busy. Retrying in {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue
            raise e
        except APIError as e:
            # check for API errors
            print(f"Gemini API Error occurred: {e.message} (Status: {e.code})")
            raise e
      
def generate_stoic_reflection(stoic_quotation: str) -> str:
    # Fetch API from GitHub secrets
    api_key = os.environ.get("LLM_API_KEY")
    MODEL_ID = 'gemini-3.6-flash'
    MAX_RETRIES = 3
    if not api_key:
        print("Error: LLM_API_KEY environment variable not found.")
        return
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    # Craft prompt
    chat_prompt = (
        f"Act as a modern Stoic philosopher who wants to share an interpretion of the following quotation: "
        f"{stoic_quotation} with a general audience. "
        "Restate the quotation and, if necessary, add who the author is. Then follow that with a 3-sentence "
        "practical explanation and one actionable exercise for today. "
        "Keep the tone grounded and clear."
    )
    # Initiate a chat
    chat = client.chats.create(model=MODEL_ID)
    for attempt in range(MAX_RETRIES):
        try:
            # Request the interpretation in chat
            chat_response = chat.send_message(chat_prompt)
            # Get the interpretation into text
            reflection_text = chat_response.text
            # set the date of the daily reflection
            current_date = datetime.now().strftime("%Y-%m-%d")
            # append the result to a markdown file that serves as a log of all reflections
            with open("daily_reflections_log.md", "a", encoding = "utf-8") as file:
                file.write(f"\n\n## Daily Reflection for {current_date}\n")
                file.write(reflection_text)
            # prepare the content to go into the updated readme
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
            return reflection_text
        except ServerError as e:
            # check any 500 level error
            if e.code >= 500 and attempt < MAX_RETRIES - 1:
                sleep_time = (attempt + 1) * 5
                print(f"Gemini API 503 busy. Retrying in {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue
            raise e
        except APIError as e:
            # check for API errors
            print(f"Gemini API Error occurred: {e.message} (Status: {e.code})")
            raise e

if __name__ == "__main__":
    today_quotation = fetch_and_check_quote()
    generate_stoic_reflection(today_quotation)
