# IntelliCoach Pro ✨

**Your Intelligent AI Career Partner to Navigate Your Professional Journey**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn- ASGI-purple?logo=python&logoColor=white)](https://www.uvicorn.org/)

IntelliCoach Pro is a FastAPI-based web application designed to act as an AI-powered career coach. It engages users in a conversational manner to understand their career aspirations, current skills, and goals, providing personalized advice, resources, and insights to help them advance professionally.

<!-- TODO: Add a GIF or screenshot of the chat interface in action! -->
<!-- Example: (Replace with your actual GIF/Screenshot) -->
<p align="center"><img src="https://github.com/kayung-developer/IntelliCoach-Pro/blob/main/Screenshot%20(58).png" alt="IntelliCoach Pro Demo" width="700"></p>
<p align="center"><img src="https://github.com/kayung-developer/IntelliCoach-Pro/blob/main/Screenshot%20(59).png" alt="IntelliCoach Pro Demo" width="700"></p>
<!-- Consider using tools like LICEcap (Windows/macOS), Kap (macOS), or ScreenToGif (Windows) to create a short demo GIF. -->

## 🚀 Key Features

*   **Conversational Interface:** Smooth, chat-based interaction for a natural user experience.
*   **Personalized Onboarding:** Gathers user's name, current role, and desired career path.
*   **In-Depth Career Path Exploration:**
    *   Detailed information for roles like Software Engineer, Data Scientist, Product Manager.
    *   Responsibilities, required skills (technical & soft).
    *   Average salary ranges.
    *   Common next career steps.
    *   Curated learning resources (courses, books, websites).
    *   Interview focus areas and example project ideas.
*   **Skill Gap Analysis:** Compares user's listed skills against requirements for their desired role.
*   **Targeted Learning Resources:** Suggests resources based on desired role and specific skill queries.
*   **Interview Preparation:** Provides general interview best practices and role-specific tips.
*   **Quick Replies:** Contextual suggestions to guide the conversation and make interaction easier.
*   **Session Management:** Remembers user context within a session using browser cookies and a backend SQLite database.
*   **Chat History:** Stores conversation history in SQLite for persistence.
*   **Dynamic UI Updates:** Frontend updates user name and displays quick replies based on AI responses.
*   **Markdown Support:** AI responses are rendered with basic Markdown for better readability (bold, italics, lists, links).

## 🛠️ Tech Stack

*   **Backend:**
    *   **Python 3.8+**
    *   **FastAPI:** For building the robust and efficient API.
    *   **Uvicorn:** ASGI server to run the FastAPI application.
*   **Database:**
    *   **SQLite:** For lightweight, file-based storage of user profiles and chat history.
*   **Frontend:**
    *   **HTML5**
    *   **CSS3:** For modern styling and layout.
    *   **Vanilla JavaScript:** For dynamic chat interactions, API calls, and DOM manipulation.
*   **Data:**
    *   In-memory Python dictionary (`CAREER_PATHS`) for detailed career information.
*   **Logging:** Python's built-in `logging` module.

## 🏁 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.8 or higher
*   `pip` (Python package installer)
*   A web browser

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kayung-developer/IntelliCoach-Pro.git # Replace YOUR_USERNAME
    cd IntelliCoach-Pro
    ```

2.  **Create and activate a virtual environment (recommended):**
    *   On macOS and Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    Create a `requirements.txt` file with the following content:
    ```txt
    fastapi
    uvicorn[standard]
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    Assuming your main Python file is named `coach.py` (as inferred from `uvicorn.run("coach:app"...)`):
    ```bash
    uvicorn coach:app --reload
    ```
    The `--reload` flag enables auto-reloading when code changes, which is useful for development.

5.  **Access IntelliCoach Pro:**
    Open your web browser and navigate to: `http://127.0.0.1:8000`

The application will automatically initialize the `intelligent_career_coach.db` SQLite database if it doesn't exist.

## ⚙️ How It Works

1.  **Client-Side (Browser):**
    *   The user interacts with an HTML/CSS/JS frontend.
    *   User messages are captured via an input field.
    *   JavaScript sends the message to the FastAPI backend (`/chat` endpoint) via a `POST` request.
    *   It then receives the AI's response and dynamically updates the chat interface, including rendering quick replies.

2.  **Backend (FastAPI):**
    *   **Session Management:** Uses HTTP cookies (`session_id`) to identify users. New sessions are created if no valid `session_id` is found.
    *   **User Profile:**
        *   User data (name, roles, skills, current conversation stage) is fetched from an in-memory cache (`USER_CONTEXT`) and backed by an SQLite database (`users` table).
        *   Profiles are updated as the conversation progresses.
    *   **Chat History:** Each user message and AI reply is logged into the `chat_history` table in SQLite.
    *   **AI Response Generation (`generate_ai_response` function):**
        *   Performs simplified intent recognition based on keywords and the user's current conversation stage (`current_stage`).
        *   Leverages the `CAREER_PATHS` dictionary to provide detailed information about roles, skills, resources, etc.
        *   Crafts a contextual response, potentially including quick reply options.
    *   **API Endpoint (`/chat`):**
        *   Receives the user's message.
        *   Logs the user message.
        *   Calls `generate_ai_response` to get the AI's reply.
        *   Logs the AI reply.
        *   Returns the AI's reply (content, type, metadata) as a JSON response.
    *   **Database Initialization (`init_db`):** Creates necessary SQLite tables (`users`, `chat_history`) on application startup if they don't exist.

3.  **Data Flow:**
    *   User Input -> JS Client -> FastAPI `/chat` -> `generate_ai_response` -> (Read `CAREER_PATHS`, Read/Write `USER_CONTEXT`/SQLite) -> JS Client -> UI Update.

## 🧩 Key Code Components (in `coach.py`)

*   **`CAREER_PATHS` (dict):** The knowledge base for different career roles. Easily extensible.
*   **`init_db()`:** Sets up the SQLite database tables.
*   **`get_user_profile(session_id)` & `update_user_profile(session_id, data)`:** Manage user state, syncing with the in-memory `USER_CONTEXT` and the SQLite database.
*   **`generate_ai_response(session_id, user_message)`:** The core logic for understanding user input and generating appropriate AI responses. This function acts as the "brain" of the coach.
*   **`generate_html_content(session_id)`:** Dynamically generates the main HTML page, including embedding chat history.
*   **`render_markdown(text)`:** A simple Markdown-to-HTML converter for AI responses.
*   **`UserSessionManager` (class):** Helper methods for creating and checking user sessions in the database.
*   **FastAPI Endpoints:**
    *   `@app.get("/")`: Serves the main chat page.
    *   `@app.post("/chat")`: Handles incoming chat messages and returns AI responses.
*   **Frontend JavaScript (embedded in HTML):**
    *   `handleSendMessage()`: Manages sending user messages and displaying AI responses.
    *   `addMessageToChat()`: Adds new messages to the chat UI.
    *   `showTypingIndicator()` / `hideTypingIndicator()`: UI enhancements.
    *   `handleQuickReply()`: Processes user clicks on quick reply buttons.
    *   `renderClientMarkdown()`: Client-side Markdown rendering for consistency.

## 🚀 Future Enhancements & Roadmap

*   **Expand Career Paths:** Add more roles to the `CAREER_PATHS` data (e.g., UX Designer, Cybersecurity Analyst, Cloud Engineer).
*   **Advanced NLP/Intent Recognition:** Integrate a more sophisticated NLP library (e.g., spaCy, NLTK) or a small LLM for better understanding of user intent and entity extraction.
*   **LLM Integration:** For more dynamic and nuanced responses, integrate with a local LLM (e.g., via Ollama) or a cloud-based LLM API (e.g., OpenAI, Gemini).
*   **Personalized Learning Roadmaps:** Generate step-by-step learning plans based on skill gaps.
*   **User Accounts:** Implement proper user authentication for persistent profiles across devices/sessions.
*   **Resource Linking & Validation:** Check for broken links in learning resources and potentially categorize them better.
*   **Mock Interview Practice:** Add a module for users to practice answering common interview questions.
*   **Progress Tracking:** Allow users to mark skills as "learned" or "in progress."
*   **Enhanced UI/UX:** Improve the visual design and user experience with more interactive elements.
*   **Deployment:** Instructions and configurations for deploying to platforms like Docker, Heroku, or AWS/GCP/Azure.

## 🙌 Contributing

Contributions are welcome! If you have ideas for improvements or want to add new features, please feel free to:

1.  **Fork the repository.**
2.  **Create a new branch** for your feature or bug fix:
    ```bash
    git checkout -b feature/your-awesome-feature
    ```
3.  **Make your changes** and commit them with clear, descriptive messages:
    ```bash
    git commit -m "Add: Your awesome feature"
    ```
4.  **Push your changes** to your forked repository:
    ```bash
    git push origin feature/your-awesome-feature
    ```
5.  **Open a Pull Request** to the main repository.

Please ensure your code adheres to the project's coding style and includes relevant tests if applicable.

You can also open an issue to discuss potential changes or report bugs.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details (you'll need to create this file, a standard MIT license is a good default).

---

*Built with ❤️ and Python by [Pascal Aondover]*


Next Steps for You:

Create requirements.txt: As mentioned in the "Installation & Setup" section.

Create LICENSE.md: Choose a license (MIT is common and permissive). You can find MIT license templates online.

Replace Placeholders:

kayung-developer in the clone URL.

[Pascal Aondover] at the bottom.

Crucially: Add a screenshot or GIF! This will make your README much more appealing.

Verify Filename: Ensure coach.py is indeed the name of your main Python file.

Push to GitHub: Commit this README.md and other files to your GitHub repository.

This README provides a solid foundation. As your project evolves, remember to update it! Good luck!
