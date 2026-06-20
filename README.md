---
page_type: sample
languages:
  - azdeveloper
  - python
  - bicep
  - html
  - css
  - scss
products:
  - azure
  - azure-app-service
  - azure-postgresql
  - azure-virtual-network
urlFragment: msdocs-fastapi-postgresql-sample-app
name: Deploy FastAPI application with PostgreSQL on Azure App Service (Python)
description: This project is for research at Cornell Tech - a health insights application powered by FastAPI and PostgreSQL.
---

<!-- YAML front-matter schema: https://review.learn.microsoft.com/en-us/help/contribute/samples/process/onboarding?branch=main#supported-metadata-fields-for-readmemd -->

# Health Insight App - Backend API

A FastAPI-powered backend application that provides health insights and AI-driven chat features. This is the backend REST API that powers the Health Insight application.

## What You'll Need Before Starting

Make sure you have these installed on your computer:

- **Python 3.9 or higher**: [Download Python](https://www.python.org/downloads/)
- **PostgreSQL database**: Either [install locally](https://www.postgresql.org/download/) OR use a cloud database like Azure PostgreSQL
- **Git**: To clone this repository

Verify your installation by opening a terminal and running:
```bash
python3 --version
pip3 --version
psql --version  # Only needed if installing PostgreSQL locally
```

## Quick Start: Running the Application

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd health-insight-app-cornell-2025-Backend
```

### Step 2: Set Up Your Environment Variables

Create a `.env` file in the project root with your database connection details:

```bash
# Option A: Copy the sample file and edit it
cp .env.sample .env

# Then edit .env with your database details:
PGDATABASE=health_insights_db
PGHOST=localhost          # Or your database server hostname
PGPORT=5432              # Default PostgreSQL port
PGUSER=postgres          # Your database username
PGPASSWORD=your_password     # Your database password
```

**Need a quick PostgreSQL database for testing?**
- **Option 1**: Install PostgreSQL locally and create a database named `health_insights_db`
- **Option 2**: Use Azure PostgreSQL or another cloud service
- **Option 3**: Use Docker: `docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres`

### Step 3: Install Python Dependencies

Open your terminal in the project root and run:

```bash
# Create a virtual environment (recommended)
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r src/requirements.txt

# Install the app as an editable package
pip install -e src
```

**What this does:**
- `venv` = isolated Python environment to avoid conflicts with other projects
- `pip install` = downloads and installs all the Python libraries this app needs (FastAPI, SQLAlchemy, etc.)

### Step 4: Set Up the Database

Initialize the database with tables and seed data:

```bash
python3 src/fastapi_app/seed_data.py
```

This creates the necessary database tables and prepares the database for your application.

### Step 5: Start the Development Server

```bash
python3 -m uvicorn fastapi_app.app:app --reload --port 8000
```

**Success!** Your backend is now running. You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Step 6: Test the API

Open your browser and visit:
- **API Documentation (Interactive)**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

The `/docs` page is interactive - you can test API endpoints right from your browser!

## Common Endpoints

Once the server is running, here are some endpoints you can test:

- **Login**: `POST /auth/login`
  ```json
  {
    "username": "testuser1",
    "password": "password"
  }
  ```

- **Chat with AI**: `POST /chat`
  - Send messages to get AI-powered health insights

- **View API Documentation**: `GET /docs`
  - Interactive interface to explore all available endpoints

## Troubleshooting

### Error: "Database connection failed"
- ✓ Check that PostgreSQL is running
- ✓ Verify your `.env` file has correct database credentials
- ✓ Ensure the database name in PGDATABASE exists in PostgreSQL

### Error: "Module 'fastapi_app' not found"
- ✓ Run `pip install -e src` in the project root
- ✓ Make sure your virtual environment is activated

### Error: "Port 8000 already in use"
- ✓ Use a different port: `python3 -m uvicorn fastapi_app.app:app --reload --port 8001`

### Application is running but won't connect
- ✓ Make sure your `.env` file is in the project root (same folder as README.md)
- ✓ Verify CORS settings in `src/fastapi_app/app.py` if connecting from a frontend

## Stop the Development Server

Press `Ctrl+C` in your terminal to stop the server.

## Next Steps

- Check the interactive API docs at http://localhost:8000/docs
- Explore the code structure in `src/fastapi_app/`
- Read the individual module docstrings for specific features

## Using GitHub Codespaces (Easy Alternative)

If you want to skip local setup:

1. Fork this repository to your account
2. Click **Code** → **Codespaces** → **+** to create a new codespace
3. In the codespace terminal, run:
   ```bash
   cp .env.sample.devcontainer .env
   pip install -r src/requirements.txt
   pip install -e src
   python3 src/fastapi_app/seed_data.py
   python3 -m uvicorn fastapi_app.app:app --reload --port 8000
   ```

## Deploying to Production

This app is configured for Azure App Service deployment. See `.github/` and `.devcontainer/` for deployment configuration details.

1. When you see the message `Your application running on port 8000 is available.`, click **Open in Browser**.

## Running locally

If you're running the app inside VS Code or GitHub Codespaces, you can use the "Run and Debug" button to start the app.

```sh
python3 -m uvicorn fastapi_app:app --reload --port=8000
```

## Deployment

This repo is set up for deployment on Azure via Azure App Service.

Steps for deployment:

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/) and create an Azure Subscription.
2. Install the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd). (If you open this repository in Codespaces or with the VS Code Dev Containers extension, that part will be done for you.)
3. Login to Azure:

   ```shell
   azd auth login
   ```

4. Provision and deploy all the resources:

   ```shell
   azd up
   ```

   It will prompt you to provide an `azd` environment name (like "myapp"), select a subscription from your Azure account, and select a location (like "eastus"). Then it will provision the resources in your account and deploy the latest code. If you get an error with deployment, changing the location can help, as there may be availability constraints for some of the resources.

5. When `azd` has finished deploying, you'll see an endpoint URI in the command output. Visit that URI, and you should see the front page of the app! 🎉

6. When you've made any changes to the app code, you can just run:

   ```shell
   azd deploy
   ```

## Getting help

If you're working with this project and running into issues, please post in [Issues](/issues).
