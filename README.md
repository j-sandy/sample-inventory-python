# E-commerce Inventory Management API

This project implements a backend REST API for managing inventory in an e-commerce website. It is built using FastAPI and utilizes an in-memory database for data storage. The API includes features for user authentication, session management, and comprehensive CRUD (Create, Read, Update, Delete) operations for inventory items, along with flexible search capabilities.

## Features

*   **User Authentication and Session Management:** Secure login and logout functionalities with session tokens.
*   **Item CRUD Operations:**
    *   Add new inventory items with details like name, item-code, quantity, procurement date, etc.
    *   Update existing item details.
    *   Delete items from the inventory.
*   **Flexible Item Search:** Fetch item details based on item-code, name, procurement date, and expiry date.
*   **In-Memory Data Storage:** Uses Python dictionaries for a simple, fast, and ephemeral database.
*   **Automatic API Documentation:** Integrated Swagger UI and ReDoc for interactive API exploration and testing.
*   **Containerization with Docker:** Easy deployment and environment consistency using Docker.

## Technologies Used

*   **Python:** Version 3.11+
*   **FastAPI:** Modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **Uvicorn:** An ASGI server for running FastAPI applications.
*   **Pydantic:** Data validation and settings management using Python type hints.

## Setup and Installation

Follow these steps to get the project up and running on your local machine.

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPOSITORY_URL_HERE]
    cd sample-inventory-python
    ```
    *(Replace `[YOUR_REPOSITORY_URL_HERE]` with the actual URL of your Git repository once it's hosted.)*

2.  **Create and activate a virtual environment:**
    It's recommended to use a virtual environment to manage project dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    Install all required Python packages using `pip`.
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

You can run the FastAPI application either directly using Uvicorn or via Docker.

### Local Development

1.  **Activate your virtual environment:**
    ```bash
    source venv/bin/activate
    ```
2.  **Start the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```
    The application will be accessible at `http://127.0.0.1:8000`. The `--reload` flag enables auto-reloading on code changes.

### Docker

1.  **Build the Docker image:**
    Navigate to the project root directory (where `Dockerfile` is located) and run:
    ```bash
    docker build -t inventory-api .
    ```
2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 inventory-api
    ```
    The application will be accessible at `http://localhost:8000`.

## API Documentation

FastAPI automatically generates interactive API documentation.

*   **Swagger UI:** Access at `http://127.0.0.1:8000/docs` (or `http://localhost:8000/docs` for Docker).
*   **ReDoc:** Access at `http://127.0.0.1:8000/redoc` (or `http://localhost:8000/redoc` for Docker).

## API Endpoints

All endpoints requiring authentication expect a `session_token` in the request headers.

### Authentication

*   **`POST /login`**
    *   **Description:** Authenticates a user and returns a session token.
    *   **Request Body:** `{"username": "admin", "password": "password"}`
    *   **Response:** `{"session_token": "..."}`
*   **`POST /logout`**
    *   **Description:** Ends the current user session.
    *   **Headers:** `session_token: YOUR_SESSION_TOKEN`

### Item Management

*   **`POST /items`**
    *   **Description:** Adds a new inventory item.
    *   **Headers:** `session_token: YOUR_SESSION_TOKEN`
    *   **Request Body Example:**
        ```json
        {
            "name": "Laptop",
            "item_code": "LAP001",
            "image": "http://example.com/laptop.jpg",
            "description": "High performance laptop",
            "quantity": 10,
            "procurement_date": "2023-01-15",
            "manufacturing_date": "2022-12-01",
            "expiry_date": null
        }
        ```
*   **`PUT /items/{item_code}`**
    *   **Description:** Updates details of an existing inventory item.
    *   **Headers:** `session_token: YOUR_SESSION_TOKEN`
    *   **Path Parameter:** `item_code` (e.g., `LAP001`)
    *   **Request Body:** Full updated item details (ensure `item_code` in body matches path).
*   **`DELETE /items/{item_code}`**
    *   **Description:** Deletes an inventory item.
    *   **Headers:** `session_token: YOUR_SESSION_TOKEN`
    *   **Path Parameter:** `item_code` (e.g., `LAP001`)
*   **`GET /items/{item_code}`**
    *   **Description:** Fetches details of a single item by its item code.
    *   **Headers:** `session_token: YOUR_SESSION_TOKEN`
    *   **Path Parameter:** `item_code` (e.g., `LAP001`)
*   **`GET /items/search/`**
    *   **Description:** Searches for items based on query parameters.
    *   **Headers:** `session_token: YOUR_SESSION_TOKEN`
    *   **Query Parameters (Optional):**
        *   `name`: Filter by item name (case-insensitive partial match).
        *   `procurement_date`: Filter by exact procurement date (e.g., `2023-01-15`).
        *   `expiry_date`: Filter by exact expiry date (e.g., `2024-12-31`).

## Authentication Credentials

*   **Default Username:** `admin`
*   **Default Password:** `password`

## Project Structure

*   `main.py`: The main FastAPI application file containing all API endpoints.
*   `models.py`: Defines the Pydantic models for `User`, `LoginRequest`, `LoginResponse`, and `Item`.
*   `requirements.txt`: Lists all Python dependencies required for the project.
*   `Dockerfile`: Defines the Docker image for containerizing the application.
*   `.gitignore`: Specifies files and directories to be ignored by Git (e.g., `venv/`, `metadata/`).
