# 🚀 MadridistaAI Bot Deployment Guide

## **Overview**
This guide covers deploying your MadridistaAI Telegram bot to various platforms for 24/7 operation.

## **🆓 Option 1: Railway (Recommended - Free Tier)**

### **Step 1: Prepare Your Code**
1. **Push to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial MadridistaAI bot"
   git branch -M main
   git remote add origin https://github.com/yourusername/madridista-bot.git
   git push -u origin main
   ```

### **Step 2: Deploy on Railway**
1. **Visit** [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **Click** "New Project"
4. **Select** "Deploy from GitHub repo"
5. **Choose** your `madridista-bot` repository
6. **Add Environment Variables**:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `OPENAI_API_KEY` = your OpenAI key
7. **Deploy** - Railway will automatically build and run your bot

### **Step 3: Verify Deployment**
- Check Railway dashboard for deployment status
- Bot will start automatically and stay running

---

## **🆓 Option 2: Render (Free Tier Available)**

### **Step 1: Prepare for Render**
1. **Ensure** `requirements.txt` is up to date
2. **Verify** `Procfile` exists (already created)

### **Step 2: Deploy on Render**
1. **Visit** [render.com](https://render.com)
2. **Sign up** and connect GitHub
3. **Click** "New +" → "Web Service"
4. **Connect** your GitHub repo
5. **Configure**:
   - **Name**: `madridista-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 main_telegram.py`
6. **Add Environment Variables**:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
7. **Deploy**

---

## **💰 Option 3: DigitalOcean App Platform**

### **Step 1: Prepare for DigitalOcean**
1. **Ensure** all files are committed to GitHub
2. **Verify** `railway.json` exists (already created)

### **Step 2: Deploy on DigitalOcean**
1. **Visit** [cloud.digitalocean.com](https://cloud.digitalocean.com)
2. **Go to** "Apps" section
3. **Click** "Create App"
4. **Connect** your GitHub repository
5. **Configure**:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python3 main_telegram.py`
6. **Add Environment Variables**
7. **Deploy**

---

## **🖥️ Option 4: VPS with Systemd (Most Control)**

### **Step 1: Set Up VPS**
1. **Create** a VPS (DigitalOcean, Linode, Vultr, etc.)
2. **SSH** into your server:
   ```bash
   ssh root@your-server-ip
   ```

### **Step 2: Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install git
sudo apt install git -y
```

### **Step 3: Deploy Your Bot**
```bash
# Clone your repository
git clone https://github.com/yourusername/madridista-bot.git
cd madridista-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env
nano .env  # Edit with your real tokens
```

### **Step 4: Set Up Systemd Service**
```bash
# Copy service file
sudo cp madridista-bot.service /etc/systemd/system/

# Edit service file with your username and paths
sudo nano /etc/systemd/system/madridista-bot.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable madridista-bot
sudo systemctl start madridista-bot

# Check status
sudo systemctl status madridista-bot
```

### **Step 5: Monitor and Manage**
```bash
# View logs
sudo journalctl -u madridista-bot -f

# Restart service
sudo systemctl restart madridista-bot

# Stop service
sudo systemctl stop madridista-bot
```

---

## **🔧 Environment Variables Setup**

### **Required Variables**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

### **Optional Variables**
```bash
DRY_RUN=false
LOG_LEVEL=INFO
```

---

## **📊 Monitoring & Maintenance**

### **Health Checks**
- **Railway/Render**: Built-in health monitoring
- **VPS**: Use systemd status and journalctl

### **Logs**
- **Railway**: Dashboard logs
- **Render**: Dashboard logs  
- **VPS**: `sudo journalctl -u madridista-bot -f`

### **Updates**
1. **Push** changes to GitHub
2. **Redeploy** (automatic on Railway/Render)
3. **VPS**: `git pull && sudo systemctl restart madridista-bot`

---

## **🚨 Troubleshooting**

### **Common Issues**
1. **Bot not responding**: Check environment variables
2. **Import errors**: Verify requirements.txt
3. **Service won't start**: Check systemd logs
4. **Memory issues**: Consider upgrading VPS plan

### **Debug Commands**
```bash
# Test locally
python3 test_telegram.py

# Check service status
sudo systemctl status madridista-bot

# View recent logs
sudo journalctl -u madridista-bot --since "1 hour ago"
```

---

## **💡 Recommendations**

- **Start with Railway** (easiest, free)
- **Move to VPS** when you need more control
- **Use systemd** for reliable 24/7 operation
- **Monitor logs** regularly
- **Set up alerts** for service failures

---

## **🎯 Next Steps**

1. **Choose** your deployment platform
2. **Follow** the specific steps above
3. **Test** your deployed bot
4. **Monitor** performance and logs
5. **Scale** as needed

¡Hala Madrid! Your bot will be running 24/7! 🤍⚽
