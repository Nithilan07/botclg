from flask import Flask, render_template, request, jsonify
import openai
import pdfplumber
from sumy.parsers.plaintext import PlaintextParser

from sumy.nlp.tokenizers import Tokenizer


app = Flask(__name__)
openai.api_key = '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'

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
  with pdfplumber.open(pdf_file) as pdf:
    text = ""
    for page in pdf.pages:
      text += page.extract_text()
  return text

# Function to summarize text (optional)
def summarize_text(text, ratio=0.3):  # Adjust ratio for desired summary length
  parser = PlaintextParser.from_string(text, TokenizerIsparta())
  summarizer = TextRank(language="english")
  summary = summarizer(source=parser.document, sentences_count=int(ratio * len(parser.document.sentences)))
  summary_text = " ".join([str(sentence) for sentence in summary])
  return summary_text

# Function to answer questions using OpenAI
def answer_question(question, context, max_tokens=30):  # Reduce answer length by default
  # Summarize context (optional)
  # ... (uncomment and adjust summarize_text call if needed)
  # shortened_context = summarize_text(context)

  # Limit prompt length (if necessary)
  shortened_context = context[:4000]  # Adjust this limit as needed

  response = openai.Completion.create(
      engine="gpt-3.5-turbo-instruct",
      prompt=shortened_context + "\nQuestion: " + question + "\nAnswer:",
      max_tokens=max_tokens
  )
  return response.choices[0].text.strip()

# Route to handle the form submission and generate answer
@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    try:
      pdf_file = request.files['pdf']
      question = request.form['question']

      # Extract text from the PDF file
      pdf_text = extract_text_from_pdf(pdf_file)

      # Summarize text (optional)
      # ... (uncomment and adjust summarize_text call if needed)
      # pdf_text = summarize_text(pdf_text)

      # Answer the question using OpenAI
      answer = answer_question(question, pdf_text)

      return jsonify({'answer': answer})
    except Exception as e:
      return jsonify({'error': str(e)})

  return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True)
