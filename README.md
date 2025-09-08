<p align="center">
  <img src="https://raw.githubusercontent.com/jgamboa-fuentes/msl-ai-summarizer-azure2/main/static/assets/dmLogo.png" alt="Data Management Logo" width="150">
</p>

# MSL Insights AI Analyser

**Author**: Enrique Gamboa, Sep 8 2025

This web application is an AI-powered tool designed to accelerate the analysis of Medical Science Liaison (MSL) insights. It allows users to upload an Excel file containing medical statements and automatically generates three distinct summaries or classifications for each statement using the power of the OpenAI API.

## Live Demo

You can test the deployed application here:

[msl-ai-summarizer-azure-dyabhge8a9c4a4aa.canadacentral-01.azurewebsites.net](http://msl-ai-summarizer-azure-dyabhge8a9c4a4aa.canadacentral-01.azurewebsites.net)

## How It Works

The application follows a simple but powerful workflow to process user data securely and efficiently.

1.  **File Upload**: The user visits the web interface and uploads an Excel file. The frontend is designed with a drag-and-drop zone for ease of use. The file is expected to contain a column named `"Statement (What)"`.

2.  **Backend Processing**: The file is sent to the Flask backend. The server uses the `pandas` library to read the Excel data into a DataFrame, which allows for efficient data manipulation.

3.  **Asynchronous API Calls**: For each row in the uploaded file, the application creates three separate analysis tasks—one for each of the pre-configured prompts. To handle a large number of requests efficiently and avoid API rate limits, the application uses Python's `asyncio` library. A `Semaphore` is implemented to limit the number of concurrent calls to the OpenAI API to 15 at a time.

4.  **OpenAI Integration**: Each task calls the OpenAI API. The function includes robust error handling with a retry mechanism that uses exponential backoff in case of rate limit errors, ensuring a high success rate.

5.  **Data Aggregation**: Once all the asynchronous tasks are complete, the application gathers the AI-generated responses.

6.  **Output Generation**: The three new insights are added as new columns (`'Prompt 1'`, `'Prompt 2'`, `'Prompt 3'`) to the original DataFrame. The updated DataFrame is then written to an in-memory Excel file using `XlsxWriter`.

7.  **File Download**: The newly generated Excel file, containing both the original data and the AI-generated insights, is sent back to the user's browser as a downloadable file named `summarized_insights.xlsx`.

## Technologies Used

* **Backend**: Flask, Gunicorn, Uvicorn
* **AI Integration**: OpenAI API (`gpt-4o`)
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

The three prompts used for analysis are configurable directly from the web interface. Click the **Configure Prompts** button to modify them. The prompts are saved in the browser's local storage for future sessions.
