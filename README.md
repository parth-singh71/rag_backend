# Backend RAG

## Overview

This project is designed to provide a set of APIs for Document Ingestion and RAG-driven Q&A. It allows users to upload documents, perform retrieval-augmented generation (RAG) queries, and select specific documents for answering questions instead of processing the entire dataset. The project is built using Python, Django, LangChain, ChromaDB and other relevant libraries.

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

- [Download Postman Collection](./RAG_Backend.postman_collection.json)
- Open Postman
- Click Import
- Select the provided Postman Collection JSON file.

## API Endpoints

### 1. `POST /api/documents/upload/`

- **Description**: Upload a document (PDF file) for processing.
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

### 2. `GET /api/documents/`

- **Description**: Fetch all uploaded documents.
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

### 3. `POST /api/ask/`

- **Description**: Retrieves a list of resources.
- **Request Body Parameters**:
  - `question` (required): Ask a question based on the selected documents and get an AI-generated answer.
- **Response**:
  - Status: `200 OK` on success.
  - Body:
    ```json
    {
      "question": "Can this candidate work as a software developer?",
      "answer": "Yes, this candidate can work as a software developer. They have strong skills in programming languages like Python and JavaScript, as well as experience in full stack development using frameworks such as Django and React.js. Additionally, their work experience includes leading projects and mentoring junior team members, indicating solid professional capabilities."
    }
    ```

### 4. `POST /api/documents/selection/`

- **Description**: Select specific documents for answering questions instead of using all uploaded documents.
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

### 5. `GET /api/documents/selection/`

- **Description**: Retrieve the list of currently selected documents.
- **Response**:
  - Status: `200 OK` on success.
  - Body:
    ```json
    {
      "selected_documents": [1, 2]
    }
    ```
