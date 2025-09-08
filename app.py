import os
import io
import openai
import pandas as pd
import asyncio
from flask import Flask, render_template, request, jsonify, send_file

# Create and configure the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-azure")

# Initialize the async OpenAI client
# Ensure your OPENAI_API_KEY is set as an environment variable in Azure
try:
    client = openai.AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except TypeError:
    client = None # Handle case where key is not set

# --- Concurrency Control ---
# Limits the number of concurrent API calls to avoid rate limiting
CONCURRENCY_LIMIT = 15
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)


# --- Routes ---

@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
async def summarize_file():
    """Handles file upload and processes it with controlled concurrency."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file was selected."}), 400
    if not client or not client.api_key:
        return jsonify({"error": "OpenAI API key is not configured on the server."}), 500

    try:
        df = pd.read_excel(file)
        statement_column = "Statement (What)"
        if statement_column not in df.columns:
            return jsonify({"error": f"Column '{statement_column}' not found."}), 400

        prompts = [
            request.form.get('prompt1'),
            request.form.get('prompt2'),
            request.form.get('prompt3')
        ]

        tasks = []
        for _, row in df.iterrows():
            statement = row[statement_column]
            for prompt in prompts:
                tasks.append(get_summary_with_retries(statement, prompt))

        all_results = await asyncio.gather(*tasks)

        # De-interleave the results back into the correct columns
        df['Prompt 1'] = all_results[0::3]
        df['Prompt 2'] = all_results[1::3]
        df['Prompt 3'] = all_results[2::3]

        # Save to an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='summarized_insights.xlsx'
        )

    except Exception as e:
        print(f"An error occurred in summarize_file: {e}")
        return jsonify({"error": str(e)}), 500


# --- Helper Function with Semaphore and Retry Logic ---

async def get_summary_with_retries(statement, prompt_template, max_retries=5):
    """
    Asynchronously calls the OpenAI API, respecting the semaphore
    to limit concurrency and using exponential backoff for retries.
    """
    if not statement or pd.isna(statement):
        return ""

    async with semaphore:
        base_delay = 1
        for attempt in range(max_retries):
            try:
                full_prompt = prompt_template + f' "{statement}"'
                
                response = await client.chat.completions.create(
                    model="gpt-4", # Using a standard model name
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()

            except openai.RateLimitError:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"Rate limit hit. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    print(f"Max retries reached for statement: {statement[:50]}...")
                    return "API Error: Max retries exceeded (Rate Limit)."

            except Exception as e:
                print(f"An unexpected API Error occurred: {e}")
                return f"API Error: {type(e).__name__}"

    return "API Error: Operation failed after all retries."


if __name__ == '__main__':
    # This part is useful for local testing but will be ignored by production servers like Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)