# 🚀 Quick Deploy to Railway (5 minutes!)

## **Why Railway?**
- ✅ **Free tier** available
- ✅ **Automatic deployments** from GitHub
- ✅ **No server management** needed
- ✅ **Built-in monitoring**
- ✅ **Easy environment variables**

## **⚡ 5-Minute Deployment**

### **Step 1: Push to GitHub (2 min)**
```bash
# In your football-bot directory
git init
git add .
git commit -m "MadridistaAI Telegram Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/madridista-bot.git
git push -u origin main
```

### **Step 2: Deploy on Railway (3 min)**
1. **Go to** [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **Click** "New Project"
4. **Select** "Deploy from GitHub repo"
5. **Choose** your `madridista-bot` repository
6. **Add Environment Variables**:
   - `TELEGRAM_BOT_TOKEN` = `your_telegram_bot_token_here`
   - `OPENAI_API_KEY` = `your_openai_api_key_here`
7. **Click Deploy** 🚀

### **Step 3: Test Your Bot**
- **Wait** for deployment (usually 1-2 minutes)
- **Message** your bot on Telegram
- **Try** `/start` command

## **🎯 That's It!**
Your bot is now running 24/7 on Railway's servers!

## **📊 Monitor Your Bot**
- **Railway Dashboard**: View logs and status
- **Telegram**: Test bot responses
- **Automatic Restarts**: If bot crashes, Railway restarts it

## **🔄 Updates**
- **Push** changes to GitHub
- **Railway** automatically redeploys
- **Zero downtime** updates

## **💰 Cost**
- **Free tier**: 500 hours/month
- **Paid plans**: Start at $5/month for unlimited

---

**Need help?** Check the full [DEPLOYMENT.md](DEPLOYMENT.md) guide!

¡Hala Madrid! 🤍⚽
