# ⚽ Strategic Football Insights Hub

A professional-grade predictive modeling application that analyzes historical match data to provide high-signal betting insights. Built with a focus on data integrity, premium user experience, and bilingual accessibility.

## 💎 Features

*   **Advanced Data Modeling**: Analyzes the last 10 finished matches to compute win probabilities, goal averages, clean sheet ratios, and BTTS frequency.
*   **Intelligent Search**: Normalization engine that handles accents (e.g., Atlético vs Atletico) and partial names with automatic fallback logic.
*   **Premium Glassmorphism UI**: A high-end, human-made dark theme using blurred translucent surfaces and professional sports typography (**Lexend** & **Inter**).
*   **Bilingual Support**: Full English/Arabic localization with RTL (Right-to-Left) support and premium Arabic typography (**Almarai**).
*   **Algorithmic Insight Engine**: Recommends high-value outcomes only when statistical confidence exceeds a defined threshold (>65%).
*   **Optimized Performance**: In-memory caching and optimized API routing to stay within free-tier rate limits.

## 🛠️ Tech Stack

*   **Backend**: Python / Flask
*   **Data Source**: Football-Data.org V4 API
*   **Frontend**: Vanilla HTML5 / CSS3 (Glassmorphism) / Modern JS
*   **Environment**: Dotenv for secure credential management

## 🚀 Quick Start

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Access**:
    *   Get a free API key from [Football-Data.org](https://www.football-data.org/client/register).
    *   Create a `.env` file in the root directory:
      ```env
      FOOTBALL_DATA_API_KEY=your_actual_api_key_here
      FLASK_DEBUG=True
      ```

4.  **Launch the Hub**:
    ```bash
    python app.py
    ```
    Access the application at `http://127.0.0.1:5000`

## 📂 Project Structure

*   `app.py`: Core routing engine and session management.
*   `services/api_client.py`: Data retrieval and normalization logic.
*   `services/analyzer.py`: Statistical processing and prediction algorithms.
*   `templates/`: High-end localized views.

## 🔒 Security

*   Credentials are isolated via `.env` and excluded from source control via `.gitignore`.
*   Production-ready debug toggles integrated into the environment configuration.

---
*Developed for professional match analysis and strategic simulation.*
