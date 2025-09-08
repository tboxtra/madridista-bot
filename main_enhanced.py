"""
Enhanced main.py with the new AI-first brain system.
Integrates multi-step reasoning, memory, dynamic tool selection, and proactive suggestions.
"""

import os
import json
from typing import Optional
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from openai import OpenAI

# Import the enhanced brain
from orchestrator.enhanced_brain import EnhancedFootballBrain

# Import legacy tools for fallback
from orchestrator.tools import (
    tool_next_fixture, tool_last_result, tool_live_now, tool_table, tool_form, tool_scorers,
    tool_next_lineups, tool_compare_teams, tool_compare_players
)

# Import utilities
from utils.memory import mem_for, export_context
from utils.relevance import classify_relevance
from utils.cooldown import can_speak, mark_spoken

# Environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

# Initialize the enhanced brain
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    enhanced_brain = EnhancedFootballBrain(openai_client)
    print("✅ Enhanced AI brain initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize enhanced brain: {e}")
    enhanced_brain = None

async def _remember(update, role="user"):
    """Remember conversation context."""
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    mem = mem_for(chat.id)
    mem.add(role=role, text=(msg.text or msg.caption or ""), user_id=(user.id if user else 0), username=(user.username or ""))
    if mem.should_summarize():
        mem.summarize_now()

# ---- Enhanced Command Handlers ----
async def cmd_start(update, context):
    """Enhanced start command with AI capabilities."""
    welcome_message = """🤖 ¡Hala Madrid! I'm your enhanced AI football assistant!

🧠 **AI Capabilities:**
• Multi-step reasoning for complex queries
• Context-aware conversation memory
• Dynamic tool selection based on intent
• Intelligent fallback strategies
• Proactive suggestions and insights

⚽ **What I can do:**
• Answer any football question naturally
• Remember our conversation context
• Provide personalized recommendations
• Handle complex multi-part queries
• Suggest related topics and follow-ups

Just ask me anything about football in natural language!"""
    
    await update.message.reply_text(welcome_message)

async def cmd_matches(update, context):
    """Enhanced matches command with AI processing."""
    team_name = " ".join(context.args) if context.args else "Real Madrid"
    
    if enhanced_brain:
        # Use enhanced AI processing
        result = enhanced_brain.process_query(
            query=f"Show me {team_name}'s next match",
            user_id=str(update.effective_user.id)
        )
        
        response = result['response']
        if result['suggestions']:
            suggestions_text = "\n💡 **Suggestions:**\n" + "\n".join([
                f"• {s['action']}" for s in result['suggestions'][:3]
            ])
            response += suggestions_text
        
        await update.message.reply_text(response)
    else:
        # Fallback to legacy system
        res = tool_next_fixture({"team_name": team_name})
        if res.get("ok"):
            sent_text = f"{res['when']} • {res['home']} vs {res['away']}"
            await update.message.reply_text(sent_text)
        else:
            sent_text = res.get("message", "No upcoming fixtures.")
            await update.message.reply_text(sent_text)

async def cmd_lastmatch(update, context):
    """Enhanced last match command with AI processing."""
    team_name = " ".join(context.args) if context.args else "Real Madrid"
    
    if enhanced_brain:
        result = enhanced_brain.process_query(
            query=f"Show me {team_name}'s last match result",
            user_id=str(update.effective_user.id)
        )
        
        response = result['response']
        if result['contextual_insights']:
            insights_text = "\n🔍 **Context:**\n" + "\n".join([
                f"• {i['content']}" for i in result['contextual_insights'][:2]
            ])
            response += insights_text
        
        await update.message.reply_text(response)
    else:
        # Fallback to legacy system
        res = tool_last_result({"team_name": team_name})
        if res.get("ok"):
            await update.message.reply_text(f"{res['when']}\n{res['home']} {res['home_score']} - {res['away_score']} {res['away']}")
        else:
            await update.message.reply_text(res.get("message", "No recent match found."))

async def cmd_live(update, context):
    """Enhanced live command with AI processing."""
    if enhanced_brain:
        result = enhanced_brain.process_query(
            query="Show me live football scores",
            user_id=str(update.effective_user.id)
        )
        
        response = result['response']
        if result['suggestions']:
            suggestions_text = "\n💡 **Live Updates:**\n" + "\n".join([
                f"• {s['action']}" for s in result['suggestions'][:2]
            ])
            response += suggestions_text
        
        await update.message.reply_text(response)
    else:
        # Fallback to legacy system
        res = tool_live_now({})
        if res.get("ok"):
            await update.message.reply_text(f"🔴 LIVE: {res['home']} {res['home_score']} - {res['away_score']} {res['away']} ({res['minute']}')")
        else:
            await update.message.reply_text(res.get("message", "No live matches."))

async def cmd_insights(update, context):
    """New command to show user insights and AI capabilities."""
    if not enhanced_brain:
        await update.message.reply_text("Enhanced AI features are not available.")
        return
    
    user_id = str(update.effective_user.id)
    insights = enhanced_brain.get_user_insights(user_id)
    
    # Format insights
    user_prefs = insights['user_preferences']
    conv_insights = insights['conversation_insights']
    
    insights_text = f"""🧠 **Your AI Insights:**

👤 **Profile:**
• Total queries: {user_prefs.get('total_queries', 0)}
• Engagement level: {user_prefs.get('engagement_level', 'new')}
• Favorite teams: {', '.join(user_prefs.get('favorite_teams', [])[:3])}

💬 **Conversation:**
• Total conversations: {conv_insights.get('total_conversations', 0)}
• Most common intents: {', '.join([intent for intent, count in conv_insights.get('most_common_intents', [])[:3]])}

🤖 **AI Features Used:**
• Multi-step reasoning: ✅
• Context memory: ✅
• Dynamic tool selection: ✅
• Proactive suggestions: ✅
• Intelligent fallbacks: ✅"""
    
    await update.message.reply_text(insights_text)

# ---- Enhanced Message Handler ----
async def text_router(update, context):
    """Enhanced text router with AI-first processing."""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    
    # Remember the user message
    await _remember(update, role="user")
    
    # Check if it's a group chat and if we should respond
    if update.effective_chat.type in ['group', 'supergroup']:
        if not can_speak(chat_id):
            return
        
        # Check relevance
        if not classify_relevance(text, is_group=True):
            return
        
        mark_spoken(chat_id)
    
    # Process with enhanced AI brain
    if enhanced_brain:
        try:
            # Get conversation context
            mem = mem_for(chat_id)
            conversation_context = {
                "recent_messages": mem.get_recent_messages(limit=5),
                "chat_type": update.effective_chat.type,
                "user_username": update.effective_user.username
            }
            
            # Process with enhanced brain
            result = enhanced_brain.process_query(
                query=text,
                user_id=user_id,
                context=conversation_context
            )
            
            # Send main response
            response = result['response']
            await update.message.reply_text(response)
            
            # Send suggestions if available
            if result['suggestions'] and len(result['suggestions']) > 0:
                suggestions_text = "💡 **Related topics:**\n" + "\n".join([
                    f"• {s['action']}" for s in result['suggestions'][:3]
                ])
                await update.message.reply_text(suggestions_text)
            
            # Remember the assistant response
            mem.add(role="assistant", text=response, user_id=0, username="bot")
            
            # Log processing metadata
            if os.getenv("DEBUG"):
                metadata = result['metadata']
                print(f"🤖 AI Processing: {metadata.get('processing_time', 0):.2f}s, "
                      f"Tools: {metadata.get('tools_used', [])}, "
                      f"Intent: {metadata.get('intent', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Enhanced AI processing failed: {e}")
            # Fallback to simple response
            await update.message.reply_text(
                "I had trouble processing that request. Please try again or use specific commands like /matches, /table, or /live."
            )
    else:
        # Fallback to legacy system
        try:
            response = await legacy_text_router(update, context)
            if response:
                await update.message.reply_text(response)
        except Exception as e:
            print(f"❌ Legacy processing failed: {e}")
            await update.message.reply_text(
                "I had trouble processing that request. Please try again or use specific commands like /matches, /table, or /live."
            )

async def legacy_text_router(update, context):
    """Legacy text router as fallback."""
    # This would contain the old text routing logic
    # For now, return a simple response
    return "I'm using the legacy system. Enhanced AI features are not available."

# ---- Application Setup ----
def main():
    """Main application setup with enhanced features."""
    print("🚀 Starting Enhanced AI Football Bot...")
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("matches", cmd_matches))
    app.add_handler(CommandHandler("lastmatch", cmd_lastmatch))
    app.add_handler(CommandHandler("live", cmd_live))
    app.add_handler(CommandHandler("insights", cmd_insights))
    
    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    
    print("✅ Enhanced AI Football Bot ready!")
    print("🤖 Features enabled:")
    print("   • Multi-step reasoning")
    print("   • Context-aware memory")
    print("   • Dynamic tool selection")
    print("   • Intelligent fallbacks")
    print("   • Proactive suggestions")
    print("   • User preference learning")
    
    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
