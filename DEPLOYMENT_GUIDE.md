# Deployment Guide (Hostinger VPS)

This guide walks you through deploying the Travel Itinerary Platform to a VPS (Virtual Private Server) running Ubuntu (recommended).

## Prerequisites
-   A VPS from Hostinger (Ubuntu 22.04/24.04 recommended).
-   SSH access to the VPS.
-   A domain name pointed to your VPS IP address (optional but recommended for SSL).

## Step 1: Connect to your VPS
Open a terminal on your local machine and connect via SSH:
```bash
ssh root@your_vps_ip
```

## Step 2: Initial Server Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/thegeekowll/easytravelitinerary.git
    cd easytravelitinerary
    ```
2.  Make the setup script executable and run it:
    ```bash
    chmod +x vps_setup.sh
    ./vps_setup.sh
    ```
3.  **IMPORTANT**: Log out and log back in for permission changes to take effect:
    ```bash
    exit
    ssh root@your_vps_ip
    cd easytravelitinerary
    ```

## Step 3: Configure Environment Variables
1.  Copy the example `.env` file:
    ```bash
    cp .env.example .env
    ```
2.  Edit the `.env` file with your production values:
    ```bash
    nano .env
    ```
    -   Set `ENVIRONMENT=production`.
    -   Set `DEBUG=False`.
    -   Generate a strong `SECRET_KEY` and `JWT_SECRET_KEY`.
    -   Set `POSTGRES_PASSWORD` to a strong password.
    -   Set `NEXT_PUBLIC_API_URL` to `http://your_domain_or_ip/api/v1`.

## Step 4: Start the Application
1.  Start the services using Docker Compose:
    ```bash
    docker compose --profile production up -d --build
    ```
    *Note: The `--profile production` flag enables the Nginx service.*

2.  Check the logs to ensure everything started correctly:
    ```bash
    docker compose logs -f
    ```

## Step 5: Access the Application
-   Open your browser and navigate to `http://your_vps_ip`.
-   You should see the application running.

## Step 6: SSL Setup (HTTPS) - Recommended
To secure your application with HTTPS (SSL), we recommend using **Nginx Proxy Manager** or **Certbot**.

### Option A: Certbot (Simpler for CLI)
1.  Install Certbot:
    ```bash
    sudo apt-get install certbot python3-certbot-nginx
    ```
2.  Run Certbot (requires you to have a domain pointing to the IP):
    ```bash
    sudo certbot --nginx -d yourdomain.com
    ```

### Option B: Updates in Docker
If you prefer keeping everything in Docker, you can modify the `nginx/nginx.conf` and mount certificates manually, but Option A is often easier on a VPS if you installed Nginx locally. Since we are using Docker-based Nginx, you would typically use a separate **LetsEncrypt** container or **Traefik**.

**Simplest Path for now:**
Use the provided HTTP setup, and if you need HTTPS, consider using Cloudflare (Flexible SSL) in front of your IP/Domain which handles SSL for you without changing server config.
