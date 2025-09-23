<p align="center">
  <img src="https://raw.githubusercontent.com/jgamboa-fuentes/msl-ai-summarizer-azure2/main/static/assets/dmLogo.png" alt="Data Management Logo" width="150">
</p>

# MSL Insights AI Analyser V3

**Author**: Enrique Gamboa, September 23 2025

This web application is an AI-powered tool designed to accelerate the analysis of Medical Science Liaison (MSL) insights. It allows users to upload an Excel file containing medical statements and automatically generates three distinct, sequential insights for each statement using the power of the OpenAI API.

## Live Demo

You can test the deployed application here:

[msl-ai-summarizer-azure-dyabhge8a9c4a4aa.canadacentral-01.azurewebsites.net](http://msl-ai-summarizer-azure-dyabhge8a9c4a4aa.canadacentral-01.azurewebsites.net)

## How It Works (V3 Logic)

The application follows an advanced workflow to generate multi-layered insights by first processing individual statements and then summarizing them at a group level.

1.  **File Upload**: The user visits the web interface and uploads an Excel file. The file is expected to contain a column named `"Statement (What)"`.

2.  **Backend Processing**: The file is sent to the Flask backend, where it is loaded into a Pandas DataFrame.

3.  **Asynchronous API Calls (Multi-Step Analysis)**: For each row in the uploaded file, the application performs a three-step analysis:
    * **Prompt 1 & 2 (Parallel)**: The original statement from each row is sent to the AI to generate a **Medical Insight** (Prompt 1) and a **Category** (Prompt 2) simultaneously. This is done for all rows.
    * **Grouping**: After the first two prompts are generated for every row, the entire dataset is grouped by **'Disease State'** and the newly generated **'Prompt 2' Category**.
    * **Prompt 3 (Grouped Summarization)**: For each group, all the original `"Statement (What)"` entries are combined into a single text block. This combined text is then sent to the AI with a third prompt to generate a **two-sentence summary**. This summary is then applied to all rows within that specific group, ensuring a consistent, high-level insight for related records.

4.  **OpenAI Integration**: All API calls use a robust error handling and retry mechanism with exponential backoff to ensure a high success rate. Concurrency is managed with an `asyncio` Semaphore to avoid API rate limits.

5.  **Data Aggregation**: Once all asynchronous tasks are complete, the application gathers the three new AI-generated values for each row.

6.  **Output Generation**: The three new insights are added as new columns (`'Prompt 1'`, `'Prompt 2'`, `'Prompt 3'`) to the original DataFrame. The updated DataFrame is then written to a single-sheet, in-memory Excel file.

7.  **File Download**: The newly generated Excel file, containing the original data and all three AI-generated insights, is sent back to the user's browser as a downloadable file named `summarized_insights.xlsx`.

## Version History

### V2 Logic

In the previous version, the application followed a sequential, row-by-row workflow to generate multi-layered insights.

* **Prompt 1 & 2 (Parallel)**: The original statement was sent to the AI to generate a **Medical Insight** (Prompt 1) and a **Category** (Prompt 2) simultaneously.
* **Prompt 3 (Sequential)**: The results from the first two prompts were combined into a new input. This new input was then sent to the AI with a third prompt to generate a final **Resummarization**. This created a powerful, context-aware analysis for each individual row.

## Technologies Used

* **Backend**: Flask, Gunicorn, Uvicorn
* **AI Integration**: OpenAI API (`gpt-5-nano`)
* **Data Handling**: Pandas
* **Asynchronous Operations**: `asyncio`
* **Frontend**: HTML5, Bootstrap 5, JavaScript
* **Deployment**: Azure App Service, GitHub Actions

## Local Setup and Testing

To run this project on your local machine, follow these steps:

1.  **Clone the Repository**
    ```sh
    git clone [https://github.com/jgamboa-fuentes/msl-ai-summarizer-azure2.git](https://github.com/jgamboa-fuentes/msl-ai-summarizer-azure2.git)
    cd msl-ai-summarizer-azure2
    ```

2.  **Create and Activate a Virtual Environment**
    ```sh
    # Create the environment
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\Activate

    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    Create a file named `.env` in the root of the project and add your OpenAI API key:
    ```
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```
    githubcodespace
    ```
    echo "OPENAI_API_KEY=sk-proj-xxx" > .env
    ```

6.  **Run the Application**
    ```sh
    flask run
    ```
    The application will be available at `http://12.0.0.1:5000`.

## Configuration

All three prompts used for the analysis are configurable from the web interface. Click the **Configure Prompts** button to modify them. The helper text has been updated to clarify the new grouping logic for Prompt 3.