# PaperPundit
This script is a tool for summarizing and discussing PDF documents, specifically scientific papers. It uses OpenAI's GPT-3.5-turbo model for the task of text summarization and question-answering. The primary functionality of the script involves extracting text from a PDF, generating a detailed summary of the content, and then having a back-and-forth discussion with the user about the content of the document.

## Prerequisites
### Libraries
Ensure you have the following Python libraries installed:

- os
- sys
- openai
- PyPDF2
- tqdm
- dotenv

You can install these using pip:

```shell
pip install openai PyPDF2 tqdm python-dotenv
```

### API Key
This script uses the OpenAI API, so you'll need an API key from OpenAI. Once you have that, create a `.env` file in the same directory as your script, and add the following line:

```
OPENAI_API_KEY=your_openai_api_key
```

Replace `your_openai_api_key` with your actual OpenAI API key.

## Usage
Clone the repository and navigate into the project directory. Make sure to create a `.env` file with your OpenAI API key as described in the Prerequisites section. To use the script, run the following command:

```shell
python3 paper_pundit.py pdf_path.pdf output_file_name.txt
```
Replace `pdf_path.pdf` with the path to the PDF file you want to process, and `output_file_name.txt` with the name of the text file where you want to save the results.

## Configuration
There are several constants at the top of the script that you can modify to suit your needs:

- `WORDS_PER_SECTION`: This is the number of words per section that the script will attempt to summarize at once.
- `SECTION_OVERLAP`: This is the number of words of overlap between consecutive sections.
- `CONVERSATION_MEMORY`: This is the number of previous messages (user + assistant pairs) kept as context for the model.

## Warning
Please note that the cost estimate given by the script may be way off from the actual cost. It is provided only as a rough guide and should not be relied upon for exact calculations. Always verify with OpenAI's actual cost and pricing details.

## License
This project is licensed under the MIT License.
