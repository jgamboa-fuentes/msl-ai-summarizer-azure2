import os
import io
import openai
import pandas as pd
import asyncio
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create and configure the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-azure")

# Initialize the async OpenAI client
try:
    client = openai.AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except TypeError:
    client = None

# --- Concurrency Control ---
CONCURRENCY_LIMIT = 15

# --- Routes ---


@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
async def summarize_file():
    """Handles file upload and processes it with the new Prompt 3 logic."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file was selected."}), 400
    if not client or not client.api_key:
        return jsonify(
            {"error": "OpenAI API key is not configured on the server."}), 500

    try:
        df = pd.read_excel(file)
        statement_column = "Statement (What)"
        if statement_column not in df.columns:
            return jsonify(
                {"error": f"Column '{statement_column}' not found."}), 400

        prompts_from_form = {
            'prompt1': request.form.get('prompt1'),
            'prompt2': request.form.get('prompt2'),
            'prompt3': request.form.get('prompt3')
        }

        # --- Step 1 & 2: Run Prompt 1 and Prompt 2 in parallel ---
        tasks = [
            process_prompts_1_and_2(row, statement_column, prompts_from_form)
            for _, row in df.iterrows()
        ]
        results_p1_p2 = await asyncio.gather(*tasks)
        df['Prompt 1'] = [res[0] for res in results_p1_p2]
        df['Prompt 2'] = [res[1] for res in results_p1_p2]

        # --- Step 3: New logic for Prompt 3 ---
        grouped = df.groupby(['Disease State', 'Prompt 2'])
        summary_tasks = []
        for name, group in grouped:
            # Concatenate "Prompt 1" for the group
            statements_to_summarize = " ".join(group['Prompt 1'].astype(str))
            # Create a task to get the summary for the concatenated statements
            summary_tasks.append(
                get_summary_with_retries(
                    statements_to_summarize,
                    "Provide a two-sentence summary of the following: ", # Generic prompt for summarization
                    asyncio.Semaphore(CONCURRENCY_LIMIT)
                )
            )

        # Get all the summaries
        group_summaries = await asyncio.gather(*summary_tasks)

        # Create a mapping from group name to summary
        summary_map = {name: summary for name, summary in zip(grouped.groups.keys(), group_summaries)}

        # Map the summaries back to the original DataFrame
        df['Prompt 3'] = df.apply(
            lambda row: summary_map.get((row['Disease State'], row['Prompt 2'])),
            axis=1
        )


        # Save to a single-sheet in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Detailed Insights')
        output.seek(0)

        return send_file(
            output,
            mimetype=
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='summarized_insights.xlsx')

    except Exception as e:
        print(f"An error occurred in summarize_file: {e}")
        return jsonify({"error": str(e)}), 500


async def process_prompts_1_and_2(row, statement_column, prompts):
    """
    Processes a single row for prompts 1 & 2 in parallel.
    """
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    original_statement = row[statement_column]

    p1_task = get_summary_with_retries(original_statement, prompts['prompt1'],
                                       semaphore)
    p2_task = get_summary_with_retries(original_statement, prompts['prompt2'],
                                       semaphore)

    prompt1_result, prompt2_result = await asyncio.gather(p1_task, p2_task)
    return prompt1_result, prompt2_result


async def get_summary_with_retries(statement,
                                   prompt_template,
                                   semaphore,
                                   max_retries=5):
    """
    Asynchronously calls the OpenAI API.
    """
    if not statement or (isinstance(statement, float) and pd.isna(statement)):
        return ""

    if not prompt_template:
        return "Error: Missing prompt template."

    async with semaphore:
        base_delay = 1
        for attempt in range(max_retries):
            try:
                # This logic now handles both types of prompts
                full_prompt = f'{prompt_template} The statement to analyze is: "{statement}"'

                response = await client.responses.create(
                    model="gpt-5-nano",
                    input=full_prompt,
                    reasoning={"effort": "low"},
                    text={"verbosity": "low"},
                )
                return response.output_text.strip()

            except openai.RateLimitError:
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    print(f"Rate limit hit. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    return "API Error: Max retries exceeded (Rate Limit)."
            except Exception as e:
                print(f"An unexpected API Error occurred: {e}")
                return f"API Error: {type(e).__name__}"

    return "API Error: Operation failed after all retries."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)