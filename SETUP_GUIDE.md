# Luminex Setup & Deployment Guide

This guide will walk you through installing Docker and running the Luminex AI Platform on your laptop.

---

## Step 1: Install Docker on Your Laptop

Luminex runs inside **Docker**, which ensures it works the same on your machine as it does in production.

### For Windows:
1.  **Download Docker Desktop**: Go to the [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) page and click **"Download for Windows"**.
2.  **Install**: Run the installer. Ensure the **"Use WSL 2 instead of Hyper-V"** option is checked (recommended).
3.  **Restart**: You may need to restart your computer.
4.  **Start Docker**: Open "Docker Desktop" from your Start menu and wait for the "Engine Running" green light.

### For macOS:
1.  **Download Docker Desktop**: Go to the [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) page. Choose **"Apple Chip"** if you have an M1/M2/M3 Mac, or **"Intel Chip"** for older Macs.
2.  **Install**: Open the `.dmg` file and drag Docker to your **Applications** folder.
3.  **Start Docker**: Open Docker from your Applications. Grant any requested permissions.

### For Linux (Ubuntu):
Run these commands in your terminal:
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

---

## Step 2: Configure Environment Variables

Luminex requires an API key to communicate with AI models (like GPT-4).

1.  Navigate to the `luminex` folder on your laptop.
2.  Create a file named `.env` (or open the existing one).
3.  Add your API key:
    ```env
    OPENAI_API_KEY=your_actual_key_here
    ```

---

## Step 3: Run Luminex with Docker Compose

Once Docker is running, you can launch the entire platform (Frontend, Gateway, Core, Database, and Redis) with a single command.

1.  **Open your Terminal** (or PowerShell/Command Prompt).
2.  **Navigate** to the Luminex project directory:
    ```bash
    cd path/to/luminex
    ```
3.  **Launch the platform**:
    ```bash
    docker-compose up --build
    ```
4.  **Wait**: Docker will download necessary images and build the platform. This may take a few minutes the first time.

---

## Step 4: Access the Platform

Once the terminal shows that the services are running, open your web browser:

*   **Luminex App**: [http://localhost:3000](http://localhost:3000)
*   **API Gateway**: [http://localhost:3001](http://localhost:3001)
*   **Core Engine**: [http://localhost:8000](http://localhost:8000)

---

## Step 5: Using the Expert UI

If you want to view the **Expert UI/UX Standalone Design**:
1.  Locate `luminex_ui.html` in the project folder.
2.  **Double-click** it to open it directly in your browser.
3.  Use the top-right buttons to switch between **Light, Dark, and OLED** modes.

---

## Troubleshooting
*   **Docker not running**: Ensure the Docker Desktop app is open and shows a green status.
*   **Port already in use**: If you get an error about ports 3000 or 5432, make sure you don't have other web servers or databases running on your machine.
*   **API Key missing**: If the AI doesn't respond, double-check your `.env` file for the `OPENAI_API_KEY`.
