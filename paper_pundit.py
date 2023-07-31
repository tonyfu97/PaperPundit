"""
Script to summarize a PDF and chat with the user about the contents of the PDF.

I rely on the resources:
https://platform.openai.com/docs/guides/gpt/chat-completions-api

Tony Fu, July 2023
"""
import os
import sys
import openai
from PyPDF2 import PdfReader
from tqdm import tqdm
from dotenv import load_dotenv

WORDS_PER_SECTION = 1800
SECTION_OVERLAP = 100
CONVERSATION_MEMORY = 5 # Number of previous messages keep as context for the model

def check_output_file_name(output_file_name):
    # check if file exists, if it does, ask user if they want to overwrite
    if (os.path.exists(output_file_name)):
        confirm = input("File already exists. Do you wish to overwrite? (y/n): ")
        if confirm.lower() != "y":
            while (os.path.exists(output_file_name)):
                output_file_name = input("Please enter a new file name: ")
        with open(output_file_name, "w") as file:
            file.write("") # To overwrite the file
    return output_file_name

def extract_text_from_pdf(pdf_path):
    print("Loading PDF...")
    with open(pdf_path, "rb") as file:
        pdf = PdfReader(file)
        text = ""
        for page in tqdm(pdf.pages):
            text += page.extract_text()
    return text

def calculate_approximate_cost(text_string, price_per_thousand_tokens):
    # WARNING: This is an approximation. The actual cost may be higher.
    words = text_string.split()
    word_count = len(words)
    # Approximation that 1 token is about 0.75 words, according to OpenAI (https://openai.com/pricing)
    token_count = word_count / 0.75
    cost = (token_count / 1000) * price_per_thousand_tokens
    return cost

def split_text_into_sections(text, words_per_section=WORDS_PER_SECTION, overlap=SECTION_OVERLAP):
    """Need this function because there is a token limit per request to OpenAI."""
    words = text.split()
    sections = []
    index = 0
    
    while index < len(words):
        # Determine the end index for the current section
        end_index = index + words_per_section
        # Add the section to the list
        sections.append(' '.join(words[index:end_index]))
        # Move the index, creating overlap
        index += words_per_section - overlap

    return sections

def get_total_summary(file_text, output_file_name):
    # Summarize each section individually
    sections = split_text_into_sections(file_text)
    section_summaries = []
    print("Generating summaries for each section...")
    for section_i, section in enumerate(tqdm(sections)):
        messages = []
        if section_i == 0:
            messages = [
            {"role": "system", "content": "ChatGPT, your task is to generate a detailed summary of the provided section from a research paper. Retain as much information as possible, especially the methods and results, as this summary will be used for subsequent Q&A discussions. This is the first section. You need to start by stating the full citation of the paper in APA format, and then state the abstract, and summarize the other section(s)."},
            {"role": "user", "content": section}
            ]
        else:
            messages = [
                {"role": "system", "content": "ChatGPT, your task is to generate a detailed summary of the provided section from a research paper. Retain as much information as possible, especially the methods and results. This summary will be used for subsequent Q&A discussions, so completeness is important. If the provided section is the Reference section, simply state 'This is the Reference section.'"},
                {"role": "user", "content": section}
            ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        section_summary = response.choices[0].message.content
        section_summaries.append(section_summary)
        
        with open(output_file_name, "a") as file:
            file.write(section_summary + "\n\n")
    return ' '.join(section_summaries)

def main(pdf_path, output_file_name):
    file_text = extract_text_from_pdf(pdf_path)
    
    cumulative_cost = calculate_approximate_cost(file_text, 0.0015)
    print(f"Approximate cost for processing the file: ${cumulative_cost:.4f}")
    confirm = input("Do you wish to proceed? (y/n): ")
    
    if confirm.lower() != "y":
        print("Operation cancelled.")
        return
    
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    total_summary = get_total_summary(file_text, output_file_name)
    cumulative_cost += calculate_approximate_cost(total_summary, 0.002)
    
    messages = [
            {"role": "system", "content": "You are an expert in this field. Your task is to concisely answer the provided question based on the provided summary of the paper and your own knowledge. You must fact-check, and indicate if you are unsure of the answer.'"},
            {"role": "user", "content": f"The questions will come later. Here is the Summary: {total_summary}."},
            {"role": "assistant", "content": "Understood. Please ask your question."},
            ]
    
    while True:
        current_cost = calculate_approximate_cost(' '.join([message['content'] for message in messages]), 0.003)
        cumulative_cost += current_cost
        print(f"\033[92mEstimated current cost per request: ${current_cost:.4f}. Estimated cumulative cost: ${cumulative_cost:.4f}\033[0m")
        question = input("Please ask a question, or type 'q' to quit: ").strip()
        if question.lower() in ['q', 'quit']:
            break
        
        messages.append({"role": "user", "content": question})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages
        )
        answer = response.choices[0].message.content
        messages.append({"role": "assistant", "content": answer})
        cumulative_cost += calculate_approximate_cost(answer, 0.004)
        
         # Delete the oldest user-assistant message pair but keep the total_summary
        while len(messages) > 2 * CONVERSATION_MEMORY + 3:
            del messages[2:4]

        print("ChatGPT:\n" + answer + "\n")
        
        with open(output_file_name, "a") as file:
            file.write("Question:\n" + question + "\n\n")
            file.write("ChatGPT:\n" + answer + "\n\n")

    with open(output_file_name, "a") as file:
        file.write(f"Estimated total cost: ${cumulative_cost:.4f}\n")
    print(f"Conversation saved to {output_file_name}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 paper_pundit.py pdf_path.pdf output_file_name.txt")
    else:
        pdf_path = sys.argv[1]
        output_file_name = sys.argv[2]
        output_file_name = check_output_file_name(output_file_name)
        main(pdf_path, output_file_name)
