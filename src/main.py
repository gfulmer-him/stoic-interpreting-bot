# main.py
import os
import time
from datetime import datetime
from google import genai
from google.genai.errors import ServerError, APIError

def try_gemini(prompt_instructions, chat):
    MAX_RETRIES = 5
    RETRY_DELAY = 480 # 4 minutes
    for attempt in range(MAX_RETRIES):
        try:
            # Request a response based on your prompt
            gemini_response = chat.send_message(prompt_instructions)
            # If successful, return immediately and break the loop
            return gemini_response
        # handle errors
        except (ServerError, APIError) as e:
            # extract error code
            status_code = getattr(e, 'code', None) or getattr(e, 'status_code', None)
            # is error worth trying again
            is_retryable = status_code and (status_code >= 500 or status_code == 429)            
            if is_retryable and attempt < MAX_RETRIES - 1: # wait if it's worth it
                sleep_time = (attempt + 1) * RETRY_DELAY
                print(f"Encountered status {status_code}. Retrying attempt {attempt + 1}/{MAX_RETRIES} in {sleep_time}s...")
                time.sleep(sleep_time)
                continue  # Skip to the next iteration of the loop
            # If it's a non-retryable error (e.g., 400 Bad Request, 403 Forbidden) or max retries hit
            print(f"Gemini API Error occurred: {getattr(e, 'message', str(e))} (Status: {status_code})")
            raise e

def fetch_and_check_quote(chat) -> str:
    if not os.path.exists("recently_quoted.txt"):
        open("recently_quoted.txt", "w").close()
    with open("recently_quoted.txt", "r", encoding = "utf-8") as f:
        recent_quotes = [line.strip() for line in f.readlines() if line.strip()]
    MAX_STORED_QUOTES = 21
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
    # Request a quotation
    quote_response = try_gemini(quote_prompt, chat)
    # Strip whitespace, replace actual newlines/carriage returns with a single space
    quotation_text = quote_response.text.strip().replace("\n", " ").replace("\r", "")
            # Clean up any accidental double spaces caused by the newline removal
    quotation_text = " ".join(quotation_text.split())
    recent_quotes.append(quotation_text)
    if len(recent_quotes) > MAX_STORED_QUOTES:
        recent_quotes.pop(0)  # Keep only the last number of entries, set by the variable
    with open("recently_quoted.txt", "w", encoding="utf-8") as f:
        for q in recent_quotes:
            f.write(f"{q}\n")    
    return quotation_text
      
def generate_stoic_reflection(stoic_quotation: str, chat) -> str:
    # Craft prompt
    chat_prompt = (
        f"Act as a modern Stoic philosopher who wants to share an interpretion of the following quotation: "
        f"{stoic_quotation} with a general audience. "
        "Restate the quotation and, if necessary, add who the author is. Then follow that with a 3-sentence "
        "practical explanation and one actionable exercise for today. "
        "Keep the tone grounded and clear."
    )
    # try the Gemini chat with this prompt
    chat_response = try_gemini(chat_prompt, chat)
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


if __name__ == "__main__":
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL ERROR: LLM_API_KEY environment variable not found.")
    MODEL_ID = 'gemini-3.6-flash'
    client = genai.Client(api_key=api_key)
    chat_session = client.chats.create(model=MODEL_ID)
    today_quotation = fetch_and_check_quote(chat_session)
    generate_stoic_reflection(today_quotation, chat_session)
