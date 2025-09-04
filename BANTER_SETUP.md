# 🎭 Smart Banter Setup Guide

Your MadridistaAI bot now has **intelligent group chat capabilities** that let it join conversations naturally with witty Real Madrid banter!

## 🔧 **Railway Environment Variables**

Add these to your Railway project → Variables:

### **Core Banter Settings:**
```bash
ENABLE_BANTER=true
BANTER_COOLDOWN_SEC=45           # min gap between bot messages in a chat
BANTER_PER_USER_COOLDOWN_SEC=120 # min gap per user
BANTER_MAX_PER_HOUR=15           # per chat, to avoid spam
BANTER_REPLY_PROB=0.55           # 0..1 random chance when triggered
```

### **Memory & Media Settings:**
```bash
ENABLE_MEMORY=true
MEMORY_WINDOW=20                  # how many recent msgs per chat to remember
ENABLE_MEDIA=true
MEDIA_REPLY_PROB=0.30            # chance to attach a meme/GIF when replying
```

### **Trigger Keywords:**
```bash
BANTER_KEYWORDS="real madrid,cristiano,ronaldo,cr7,vinicius,vini,bernabeu,hala madrid,bellingham,ancelotti,mbappe"
BANTER_RIVALS="barcelona,barca,messi"
```

## 🚀 **BotFather Setup**

1. **Open @BotFather** in Telegram
2. **Send `/mybots`** → choose your bot
3. **Bot Settings** → **Group Privacy**
4. **Tap "Turn off"** (Disable Privacy Mode)

Now your bot can read all group messages and join conversations!

## 🎯 **How It Works**

### **Smart Triggers:**
- **Keywords**: "Ronaldo", "Vinicius", "Real Madrid"
- **Rivals**: "Barcelona", "Messi", "Barca"
- **Mentions**: @YourBotName
- **Random**: 5% chance to chime in on Madrid-related topics

### **Human-Like Features:**
- **Conversational Memory**: Remembers last 20 messages per chat
- **Context-Aware**: Understands conversation flow
- **Typing Delays**: Simulates human typing behavior
- **Media Reactions**: Sometimes attaches memes/GIFs
- **Threaded Replies**: Responds to specific messages

### **Safety Rails:**
- **Cooldowns**: 45s between messages, 2min per user
- **Hourly Cap**: Max 15 messages per chat per hour
- **Toxicity Guard**: Filters out harsh responses
- **Per-Chat Control**: `/banteron` and `/banteroff` commands

### **Example Interactions:**
```
User: "Ronaldo is finished"
Bot: "Finished? He's got 5 Champions League titles. What have you won? 🤍"

User: "Barca cooking Madrid"
Bot: "Cooking? We're the ones with the recipe for success! 14 UCL trophies don't lie ⚽"

User: "Vinicius overrated"
Bot: "Overrated? Tell that to the defenders he's been cooking all season! 🔥"
```

## 🧪 **Testing Your Bot**

### **1. Add to Test Group:**
- Create a small test group
- Add your bot
- Make sure Group Privacy is OFF

### **2. Enable Banter:**
- Set `ENABLE_BANTER=true` in Railway
- Redeploy your service

### **3. Test Commands:**
```
/banteron  - Enable banter in current chat
/banteroff - Disable banter in current chat
```

### **4. Test Triggers:**
- "Ronaldo still the 🐐?"
- "Vini clear."
- "Barca better"
- "@YourBotName thoughts?"

## ⚙️ **Fine-Tuning**

### **If Too Chatty:**
- Lower `BANTER_REPLY_PROB` (e.g., 0.4)
- Increase `BANTER_COOLDOWN_SEC` (e.g., 60)
- Reduce `BANTER_MAX_PER_HOUR` (e.g., 10)

### **If Too Quiet:**
- Raise `BANTER_REPLY_PROB` (e.g., 0.8)
- Decrease `BANTER_COOLDOWN_SEC` (e.g., 30)
- Expand `BANTER_KEYWORDS` with more terms

### **Add More Rivals:**
```
BANTER_RIVALS="barcelona,barca,messi,atletico,atleti,griezmann"
```

## 🛡️ **Safety Features**

- **Toxicity Filter**: Blocks harsh language
- **Length Limits**: Skips long walls of text
- **Bot Detection**: Won't reply to other bots
- **Admin Control**: Easy on/off per chat
- **Rate Limiting**: Prevents spam

## 🎭 **Banter Personality**

Your bot is programmed to be:
- **Confident** - Proud of Real Madrid's achievements
- **Playful** - Witty, not mean
- **Factual** - Uses real stats and history
- **Engaging** - Joins conversations naturally
- **Respectful** - Never toxic or personal

## 🚨 **Troubleshooting**

### **Bot Not Responding:**
1. Check `ENABLE_BANTER=true`
2. Verify Group Privacy is OFF
3. Check Railway logs for errors
4. Try `/banteron` in the chat

### **Too Many Messages:**
1. Lower `BANTER_REPLY_PROB`
2. Increase cooldown values
3. Use `/banteroff` temporarily

### **Not Enough Messages:**
1. Raise `BANTER_REPLY_PROB`
2. Add more keywords
3. Decrease cooldown values

## 🎉 **Enjoy Your Smart Bot!**

Your MadridistaAI is now a **group chat superstar** that can:
- Join conversations naturally
- Defend Real Madrid with style
- Troll rivals playfully
- Stay engaging without spam
- Respect chat dynamics

**¡Hala Madrid! 🤍⚽**
