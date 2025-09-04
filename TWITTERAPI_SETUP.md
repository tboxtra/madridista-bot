# TwitterAPI.io Setup Guide

## 🚀 Why TwitterAPI.io?

- **100x cheaper** than official Twitter API ($0.15 per 1K tweets vs $100+)
- **No approval process** - start immediately
- **Real-time data** with 1000+ req/sec rate limits
- **24/7 support** and much more reliable

## 📋 Setup Steps

### 1. Get Your API Key
1. Go to [https://twitterapi.io/](https://twitterapi.io/)
2. Click "Start Free Trial" 
3. Sign up (no credit card required)
4. Get $0.1 in free credits to start
5. Copy your API key from the dashboard

### 2. Update Your .env File
```bash
# Replace this line in your .env file:
TWITTERAPI_KEY=your_actual_api_key_here
```

### 3. Test the Bot
```bash
# Set DRY_RUN=false to post real tweets
sed -i '' 's/DRY_RUN=true/DRY_RUN=false/' .env

# Run the bot
python3 main.py
```

## 💰 Pricing
- **Free trial**: $0.1 credits (no credit card)
- **Pay-as-you-go**: $0.15 per 1,000 tweets
- **No monthly fees** or hidden costs

## 🔧 API Endpoints Used
- **POST /v2/tweets** - Create new tweets
- **Rate limit**: 1000+ requests per second
- **Response time**: < 500ms average

## 🆘 Support
- **24/7 Live Chat** on twitterapi.io
- **Documentation**: [https://twitterapi.io/docs](https://twitterapi.io/docs)
- **No Twitter developer account needed!**

## ✅ Benefits Over Official API
| Feature | TwitterAPI.io | Official Twitter API |
|---------|---------------|---------------------|
| Setup Time | < 5 minutes | Weeks (approval) |
| Cost per 1K tweets | $0.15 | $100+ |
| Rate Limit | 1000+ req/sec | 300 req/15min |
| Support | 24/7 Live Chat | Almost None |
| Approval | None needed | Strict review |

Your MadridistaAI bot is now ready to use TwitterAPI.io! 🏆⚽️
