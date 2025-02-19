# Backend RAG

## Overview

This project is designed to provide a set of APIs for Document Ingestion and RAG-driven Q&A. It allows users to upload documents, perform retrieval-augmented generation (RAG) queries, and select specific documents for answering questions instead of processing the entire dataset. The project is built using Python, Django, LangChain, ChromaDB and other relevant libraries.

## Setup & Installation

### 1. Clone the Repository

```bash
git clone git@github.com:parth-singh71/rag_backend.git
cd rag-backend
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

### 5. Start Django Server

```bash
python manage.py runserver
```

The server will run at http://127.0.0.1:8000/.

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
