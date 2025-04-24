# Multi-User Corrective RAG Backend

## Overview

This project is designed to provide a robust set of APIs for **Document Ingestion** and **Advanced RAG-driven Q&A**. It allows users to upload documents, perform intelligent retrieval-augmented generation (RAG) queries, and select specific documents for answering questions instead of querying the entire dataset. It's built using Python, Django, LangChain, LangGraph, ChromaDB and other modern tools.

## Key Features

1. **Corrective RAG with LangGraph**  
   Implements a Corrective RAG workflow using **LangChain** and **LangGraph**, where retrieved context is validated. If irrelevant, the system **rephrases the query** and performs an internet search using a **ReAct agent** to get better context.

2. **JWT-based Authentication**  
   Secures all endpoints with **JSON Web Tokens (JWT)** to authenticate and authorize users effectively.

3. **Multi-user Support with Thread Context**  
   Enables multiple users to run independent sessions with support for **Thread IDs**, maintaining the **stateful conversational context** for follow-up questions.

4. **Custom Document Selection for Querying**  
   Allows users to **select specific documents** for answering questions rather than using the full corpus, improving response relevance and performance.

5. **Document Upload and Listing APIs**  
   Provides endpoints to **upload**, **list**, and **retrieve** documents. Uploaded documents are stored with metadata and made searchable using **ChromaDB**.

6. **Vector Store Integration**  
   Uses **ChromaDB** to store and retrieve documents based on **vector similarity**, ensuring accurate document matches.

7. **Extensible Architecture**  
   Designed with clean abstractions and extensible modules—ideal for enterprise-scale customizations or integrations with existing platforms.

## Tools & Libraries Used:

1. LangChain
2. LangGraph
3. Django
4. Django REST Framework
5. LLM Model - `gpt-4o-mini` provided by OpenAI

## Setup & Installation

### 1. Clone the Repository

```bash
git clone git@github.com:parth-singh71/rag_backend.git
cd rag_backend
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Add Environment Variables

Since this project uses `gpt-4o-mini` for text generation in RAG, you will need to add an API Key from OpenAI for this project to work.

#### **For Linux (Bash)**

```bash
echo 'export OPENAI_API_KEY="YOUR_API_KEY"' >> ~/.bashrc && source ~/.bashrc
```

If using a login shell, use `~/.profile` instead of `~/.bashrc`.

#### For MacOS (Bash Shell):

```bash
echo 'export OPENAI_API_KEY="YOUR_API_KEY"' >> ~/.bash_profile && source ~/.bash_profile
```

#### For MacOS (Zsh Shell):

```sh
echo 'export OPENAI_API_KEY="YOUR_API_KEY"' >> ~/.zshrc && source ~/.zshrc
```

#### For Windows (Powershell):

```powershell
setx OPENAI_API_KEY "YOUR_API_KEY"
```

Note: For Windows users, restarting the terminal (or system) is required after using setx.

### 6. Start Django Server

```bash
python manage.py runserver
```

The server will run at http://127.0.0.1:8000/.

## Running Unit Tests

This project includes unit tests to ensure API functionality. To run all tests, use:

```bash
python manage.py test
```

### Unit Test Cases Location

All unit tests are located in: `api/tests/`

### Example to run a specific test case:

```bash
python manage.py test api.tests.test_views.GenericDocumentsViewTest.test_get_all_documents
```

## Testing with Postman

- [Download Postman Collection](./RAG_Backend_V2.postman_collection.json)
- Open Postman
- Click Import
- Select the provided Postman Collection JSON file.

## API Endpoints

### Auth APIs:

#### 1. `POST /api/auth/signup/`

- **Description**: Allows users to create a new account by providing their details.
- **Request Body Parameters**:
  - `username` (required): user username.
  - `email` (required): user email address.
  - `password` (required): user password.
- **Response**:
  - Status: `200 OK` on success.
  - Body:
    ```json
    {
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0MjI5NTA4NSwiaWF0IjoxNzQxNjkwMjg1LCJqdGkiOiI3YzhmYTQ1MzE3MzQ0ZTA2OTA2ZjA5ZjQwOTIxNzQyMyIsInVzZXJfaWQiOjN9.AF3pQs7UVp-Derqm91Ed1Eyv17TqFZc6Kh35FB8foyM",
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxNjkyMDg1LCJpYXQiOjE3NDE2OTAyODUsImp0aSI6ImY1MDEwYjU0M2U5NjQ4ZmQ5YjBmOGY0NTBkYzdlNWUxIiwidXNlcl9pZCI6M30.J4lNk4DHDzsoetKM3gO4C2HdYrI6lfbIDJrvDMM6mrE",
      "user_id": 3
    }
    ```

#### 2. `POST /api/auth/login/`

- **Description**: Allows users to authenticate.
- **Request Body Parameters**:
  - `username` (required): user username.
  - `password` (required): user password.
- **Response**:
  - Status: `200 OK` on success.
  - Body:
    ```json
    {
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0MjI5NTYxOCwiaWF0IjoxNzQxNjkwODE4LCJqdGkiOiI5OWZlNTVlNTRlNjk0MzU3YTg5NjEzN2FlNjJkYmJmOSIsInVzZXJfaWQiOjJ9.0qjy00aOMvYCbZHFpMMJ85f5BeW8Yp8iSFUl4eCQtOI",
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxNjkyNjE4LCJpYXQiOjE3NDE2OTA4MTgsImp0aSI6IjY2YTVhYzBiYTgxYzQxMTU5ZjJhYTJhZWNmZWY0YWE0IiwidXNlcl9pZCI6Mn0.Edi-R29fOAt0TK4FaMkPD2TzDsDS3eto5Emy-11o_Dw",
      "user_id": 3
    }
    ```

#### 3. `POST /api/auth/token/verify/`

- **Description**: Verifies if an access token is valid or not.
- - **Request Body Parameters**:
  - `token` (required): access token.
- **Response**:
  - Status: `401 Unauthorized` on failure.
  - Body:
    ```json
    {
      "detail": "Token is invalid",
      "code": "token_not_valid"
    }
    ```

#### 4. `POST /api/auth/logout/`

- **Description**: Logs out a user.
- - **Request Body Parameters**:
  - `refresh_token` (required): refresh token obtained during login or signup.
- **Response**:
  - Status: `204 No Content` on success.

### Other APIs:

#### 1. `POST /api/documents/upload/`

- **Description**: Upload a document (PDF file) for processing.
- **Headers**:
  ```json
  {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
  }
  ```
- **Request Body Parameters**:
  - `title` (required): Document title.
  - `file` (required): PDF file to upload.
  - `description` (optional): Document description.
- **Response**:
  - Status: `201 OK` on success.
  - Body:
    ```json
    {
      "upload_status": "success",
      "message": "Document uploaded successfully",
      "data": {
        "id": 1,
        "title": "my resume",
        "description": "testing description",
        "uploaded_at": "2025-02-19T19:02:48.905794Z",
        "file": "/uploads/documents/resume_VyU0IqA.pdf"
      }
    }
    ```

#### 2. `GET /api/documents/`

- **Description**: Fetch all uploaded documents by user.
- **Headers**:
  ```json
  {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
  }
  ```
- **Response**:
  - Status: `200 OK` on success.
  - Body:
    ```json
    [
      {
        "id": 1,
        "title": "my resume",
        "description": "testing description",
        "uploaded_at": "2025-02-19T19:02:48.905794Z",
        "file": "/uploads/documents/resume_VyU0IqA.pdf"
      }
    ]
    ```

#### 3. `POST /api/ask/`

- **Description**: Ask questions and get responses via an advanced RAG-driven system.
- **Headers**:
  ```json
  {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
  }
  ```
- **Request Body Parameters**:
  - `question` (required): Ask a question based on the selected documents and get an AI-generated answer.
  - `thread_id` (required): A unique identifier used to group all interactions within the same conversational session.
- **Response**:
  - Status: `200 OK` on success.
  - Body:
    ```json
    {
      "question": "Can this candidate work as a software developer?",
      "answer": "Yes, this candidate can work as a software developer. They have strong skills in programming languages like Python and JavaScript, as well as experience in full stack development using frameworks such as Django and React.js. Additionally, their work experience includes leading projects and mentoring junior team members, indicating solid professional capabilities."
    }
    ```

#### 4. `POST /api/documents/selection/`

- **Description**: Select specific documents for answering questions instead of using all uploaded documents by user.
- **Headers**:
  ```json
  {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
  }
  ```
- **Request Body Parameters**:
  - `document_ids` (required): List of document ids to select.
- **Response**:
  - Status: `200 OK` on success.
  - Body:
    ```json
    {
      "message": "Documents selected successfully",
      "selected_documents": [1, 2]
    }
    ```

#### 5. `GET /api/documents/selection/`

- **Description**: Retrieve the list of currently selected documents for a user.
- **Headers**:
  ```json
  {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
  }
  ```
- **Response**:
  - Status: `200 OK` on success.
  - Body:
    ```json
    {
      "selected_documents": [1, 2]
    }
    ```
