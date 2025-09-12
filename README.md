<p align="center">
  <img src="https://raw.githubusercontent.com/jgamboa-fuentes/msl-ai-summarizer-azure2/main/static/assets/dmLogo.png" alt="Data Management Logo" width="150">
</p>

# MSL Insights AI Analyser V2

**Author**: Enrique Gamboa, Sep 12 2025

This web application is an AI-powered tool designed to accelerate the analysis of Medical Science Liaison (MSL) insights. It allows users to upload an Excel file containing medical statements and automatically generates three distinct, sequential insights for each statement using the power of the OpenAI API.

## Live Demo

You can test the deployed application here:

[msl-ai-summarizer-azure-dyabhge8a9c4a4aa.canadacentral-01.azurewebsites.net](http://msl-ai-summarizer-azure-dyabhge8a9c4a4aa.canadacentral-01.azurewebsites.net)

## How It Works (V2 Logic)

The application follows a sequential, row-by-row workflow to generate multi-layered insights.

1.  **File Upload**: The user visits the web interface and uploads an Excel file. The file is expected to contain a column named `"Statement (What)"`.

2.  **Backend Processing**: The file is sent to the Flask backend, where it is loaded into a Pandas DataFrame.

3.  **Asynchronous API Calls (Sequential Analysis)**: For each row in the uploaded file, the application performs a three-step analysis:
    * **Prompt 1 & 2 (Parallel)**: The original statement is sent to the AI to generate a **Medical Insight** (Prompt 1) and a **Category** (Prompt 2) simultaneously.
    * **Prompt 3 (Sequential)**: The results from the first two prompts are combined into a new input. This new input is then sent to the AI with a third prompt to generate a final **Resummarization**. This creates a powerful, context-aware analysis for each individual row.

4.  **OpenAI Integration**: All API calls use a robust error handling and retry mechanism with exponential backoff to ensure a high success rate. Concurrency is managed with an `asyncio` Semaphore to avoid API rate limits.

5.  **Data Aggregation**: Once all asynchronous tasks are complete, the application gathers the three new AI-generated values for each row.

6.  **Output Generation**: The three new insights are added as new columns (`'Prompt 1'`, `'Prompt 2'`, `'Prompt 3'`) to the original DataFrame. The updated DataFrame is then written to a single-sheet, in-memory Excel file.

7.  **File Download**: The newly generated Excel file, containing the original data and all three AI-generated insights, is sent back to the user's browser as a downloadable file named `summarized_insights.xlsx`.

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

5.  **Run the Application**
    ```sh
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Configuration

All three prompts used for the sequential analysis are configurable from the web interface. Click the **Configure Prompts** button to modify them. Helper text is included to clarify that Prompt 3 uses the output from the first two as its input.