"""
Enhanced AI Football Bot - Main Application
Now uses the enhanced AI brain with multi-step reasoning, memory, and advanced features.
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
from utils.user_manager import UserManager
from utils.api_manager import APIManager
from features.telegram_interactive import TelegramInteractiveHandler
from features.realtime_updates import RealTimeUpdateSystem

# Environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

# Initialize the enhanced brain and systems
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    enhanced_brain = EnhancedFootballBrain(openai_client)
    print("✅ Enhanced AI brain initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize enhanced brain: {e}")
    enhanced_brain = None

try:
    user_manager = UserManager()
    print("✅ User management system initialized")
except Exception as e:
    print(f"❌ Failed to initialize user manager: {e}")
    user_manager = None

try:
    api_manager = APIManager()
    print("✅ API manager initialized")
except Exception as e:
    print(f"❌ Failed to initialize API manager: {e}")
    api_manager = None

try:
    interactive_handler = TelegramInteractiveHandler()
    print("✅ Interactive features initialized")
except Exception as e:
    print(f"❌ Failed to initialize interactive handler: {e}")
    interactive_handler = None

try:
    if api_manager:
        realtime_system = RealTimeUpdateSystem(api_manager)
        print("✅ Real-time update system initialized")
    else:
        realtime_system = None
        print("⚠️ Real-time system skipped (API manager not available)")
except Exception as e:
    print(f"❌ Failed to initialize real-time system: {e}")
    realtime_system = None

async def _remember(update, role="user"):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    mem = mem_for(chat.id)
    mem.add(role=role, text=(msg.text or msg.caption or ""), user_id=(user.id if user else 0), username=(user.username or ""))
    if mem.should_summarize():
        mem.summarize_now()

# ---- Command handlers (concise, API-grounded) ----
async def cmd_start(update, context):
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
• Weather conditions for matches
• Enhanced news with sentiment analysis
• Transfer value conversions
• Market trends and analysis

Just ask me anything about football in natural language!"""
    
    await update.message.reply_text(welcome_message)

async def cmd_matches(update, context):
    res = tool_next_fixture({"team_name": " ".join(context.args) if context.args else "Real Madrid"})
    if res.get("ok"):
        sent_text = f"{res['when']} • {res['home']} vs {res['away']}"
        await update.message.reply_text(sent_text)
    else:
        sent_text = res.get("message", "No upcoming fixtures.")
        await update.message.reply_text(sent_text)
    mem_for(update.effective_chat.id).add(role="assistant", text=sent_text, user_id=0, username="bot")

async def cmd_lastmatch(update, context):
    res = tool_last_result({"team_name": " ".join(context.args) if context.args else "Real Madrid"})
    if res.get("ok"):
        await update.message.reply_text(f"{res['when']}\n{res['home']} {res['home_score']} - {res['away_score']} {res['away']}")
    else:
        await update.message.reply_text(res.get("message", "No recent match found."))

async def cmd_live(update, context):
    res = tool_live_now({})
    if res.get("ok"):
        await update.message.reply_text(f"{res['homeName']} {res['homeScore']} - {res['awayScore']} {res['awayName']} • {res.get('minute','')}'")
    else:
        await update.message.reply_text("No live match right now.")

async def cmd_table(update, context):
    comp = " ".join(context.args) if context.args else "LaLiga"
    res = tool_table({"competition": comp})
    if res.get("ok"):
        lines = ["*League Table (Top 5)*"]
        for r in res["rows"][:5]:
            lines.append(f"{r['pos']}. {r['team']}  {r['pts']} pts")
        await update.message.reply_markdown("\n".join(lines))
    else:
        await update.message.reply_text("Table data unavailable.")

async def cmd_scorers(update, context):
    comp = " ".join(context.args) if context.args else "LaLiga"
    res = tool_scorers({"competition": comp, "limit": 5})
    if res.get("ok"):
        lines = ["*Top Scorers*"]
        for s in res["rows"][:5]:
            lines.append(f"{s['player']} — {s['goals']}g ({s['team']})")
        await update.message.reply_markdown("\n".join(lines))
    else:
        await update.message.reply_text("Scorers data unavailable.")

async def cmd_form(update, context):
    team = " ".join(context.args) if context.args else "Real Madrid"
    res = tool_form({"team_name": team, "k": 5})
    if res.get("ok"):
        lines = ["*Recent Results*"]
        for m in res["results"]:
            lines.append(f"{m['when']}\n{m['home']} {m['home_score']} - {m['away_score']} {m['away']}")
        await update.message.reply_markdown("\n".join(lines))
    else:
        await update.message.reply_text("Recent results unavailable.")

async def cmd_lineups(update, context):
    team = " ".join(context.args) if context.args else "Real Madrid"
    from nlp.resolve import resolve_team
    res = tool_next_lineups({"team_id": resolve_team(team)})
    if res.get("ok"):
        h = res["home"]; a = res["away"]; ev = res["event"]
        lines = [f"*{ev['home']} vs {ev['away']}*",
                 "*Home XI:* " + ", ".join(p["name"] for p in h["xi"]),
                 "*Away XI:* " + ", ".join(p["name"] for p in a["xi"])]
        await update.message.reply_markdown("\n".join(lines))
    else:
        await update.message.reply_text(res.get("message", "Lineups unavailable."))

async def cmd_compare(update, context):
    args = " ".join(context.args) if context.args else ""
    parts = [p.strip() for p in args.split("vs")] if "vs" in args else []
    if len(parts) != 2:
        await update.message.reply_text("Usage: /compare Team A vs Team B")
        return
    res = tool_compare_teams({"team_a": parts[0], "team_b": parts[1], "k": 5})
    if res.get("ok"):
        await update.message.reply_text(f"{res['team_a']} {res['points_a']} pts vs {res['team_b']} {res['points_b']} pts • Verdict: {res['verdict']}")
    else:
        await update.message.reply_text(res.get("message", "Not enough recent matches."))

async def cmd_compareplayers(update, context):
    args = " ".join(context.args) if context.args else ""
    parts = [p.strip() for p in args.split("vs")] if "vs" in args else []
    if len(parts) != 2:
        await update.message.reply_text("Usage: /compareplayers Player A vs Player B")
        return
    res = tool_compare_players({"player_a": parts[0], "player_b": parts[1]})
    if res.get("ok"):
        a = res["a"]; b = res["b"]
        def line(p):
            g = p.get("goals"); ap = p.get("assists")
            g90 = p.get("goals_p90"); a90 = p.get("assists_p90")
            return f"{p['name']}: {g}g/{ap}a (per90: {g90}g/{a90}a)"
        await update.message.reply_text(f"{line(a)}\n{line(b)}")
    else:
        await update.message.reply_text(res.get("message", "Comparison unavailable."))

async def cmd_predict(update, context):
    team = " ".join(context.args) if context.args else "Real Madrid"
    from orchestrator.tools import tool_predict_fixture
    res = tool_predict_fixture({"team_name": team})
    if res.get("ok"):
        sent_text = res.get("prediction", "No prediction available.")
        await update.message.reply_text(sent_text)
    else:
        sent_text = res.get("message", "No match to predict.")
        await update.message.reply_text(sent_text)
    mem_for(update.effective_chat.id).add(role="assistant", text=sent_text, user_id=0, username="bot")

async def text_router(update, context):
    """Enhanced text router with AI-first processing and all new features."""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    
    # Get or create user profile
    if user_manager:
        user_profile = user_manager.get_or_create_user(
            user_id=user_id,
            username=update.effective_user.username or "",
            first_name=update.effective_user.first_name or "",
            last_name=update.effective_user.last_name or ""
        )
    
    # Remember the user message
    await _remember(update, role="user")
    
    # Check if it's a group chat and if we should respond
    is_group = update.effective_chat.type in ['group', 'supergroup']
    if is_group:
        should, conf, reason = classify_relevance(text, is_group=True)
        if not should:
            return
        
        if reason not in ("mentioned", "dm_default"):
            if not can_speak(chat_id):
                return
        
        mark_spoken(chat_id)
    
    # Check for interactive feature requests
    if interactive_handler:
        if "create a poll" in text.lower() or "poll" in text.lower():
            # Extract match data from text
            match_data = {"home_team": "Real Madrid", "away_team": "Barcelona", "match_id": f"poll_{chat_id}"}
            result = await interactive_handler.create_match_prediction_poll(update, context, match_data)
            if result.get("ok"):
                return
        
        elif "quiz" in text.lower() or "trivia" in text.lower():
            result = await interactive_handler.create_quiz_question(update, context)
            if result.get("ok"):
                return
        
        elif "compare" in text.lower() and ("team" in text.lower() or "vs" in text.lower()):
            # Extract teams from text
            teams = ["Real Madrid", "Barcelona"]  # Default
            result = await interactive_handler.create_team_comparison_poll(update, context, teams[0], teams[1])
            if result.get("ok"):
                return
    
    # Check for achievement requests
    if "achievements" in text.lower() or "stats" in text.lower():
        if user_manager:
            achievements = user_manager.get_user_achievements(user_id)
            if achievements.get("ok"):
                response = f"🏆 **Your Achievements & Stats**\n\n"
                response += f"**Earned Achievements:** {len(achievements['earned_achievements'])}\n"
                response += f"**Total Queries:** {achievements['user_stats']['total_queries']}\n"
                response += f"**Prediction Accuracy:** {achievements['user_stats']['accurate_predictions']}\n"
                response += f"**Quiz Score:** {achievements['user_stats']['quiz_accuracy']:.1f}%\n"
                response += f"**Favorite Teams:** {', '.join(achievements['user_stats']['favorite_teams'])}\n"
                await update.message.reply_text(response, parse_mode='Markdown')
                return
    
    # Process with enhanced AI brain
    if enhanced_brain:
        try:
            # Get conversation context
            mem = mem_for(chat_id)
            ctx = export_context(chat_id)
            conversation_context = {
                "recent_messages": [],
                "chat_type": update.effective_chat.type,
                "user_username": update.effective_user.username,
                "conversation_summary": ctx.get("summary", ""),
                "user_profile": user_profile.__dict__ if user_manager else {}
            }
            
            # Process with enhanced brain
            result = enhanced_brain.process_query(
                query=text,
                user_id=user_id,
                context=conversation_context
            )
            
            # Update user activity
            if user_manager:
                user_manager.update_user_activity(user_id, "query", {
                    "intent": result.get("intent", "general"),
                    "mentioned_teams": result.get("mentioned_teams", []),
                    "mentioned_players": result.get("mentioned_players", [])
                })
            
            # Send main response
            response = result['response']
            await update.message.reply_text(response, disable_web_page_preview=False, reply_to_message_id=update.message.message_id if is_group else None)
            
            # Send suggestions if available (only for complex queries)
            if (result.get('suggestions') and len(result['suggestions']) > 0 and 
                len(text) > 50 and any(keyword in text.lower() for keyword in ['compare', 'analysis', 'detailed', 'comprehensive'])):
                suggestions_text = "💡 **Related topics:**\n" + "\n".join([
                    f"• {s.get('action', s.get('message', str(s)))}" for s in result['suggestions'][:2]
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
            # Fallback to legacy system
            try:
                from orchestrator.brain import answer_nl_question
                ctx = export_context(chat_id)
                context_prefix = ""
                if ctx.get("summary"):
                    context_prefix = f"(Conversation summary context, keep consistent with this recent thread; don't repeat):\n{ctx['summary']}\n\n"
                
                reply = answer_nl_question(context_prefix + text)
                await update.message.reply_text(reply, disable_web_page_preview=False, reply_to_message_id=update.message.message_id if is_group else None)
                mem_for(chat_id).add(role="assistant", text=reply, user_id=0, username="bot")
            except Exception as e2:
                print(f"❌ Legacy processing also failed: {e2}")
                await update.message.reply_text(
                    "I had trouble processing that request. Please try again or use specific commands like /matches, /table, or /live."
                )
    else:
        # Fallback to legacy system
        try:
            from orchestrator.brain import answer_nl_question
            ctx = export_context(chat_id)
            context_prefix = ""
            if ctx.get("summary"):
                context_prefix = f"(Conversation summary context, keep consistent with this recent thread; don't repeat):\n{ctx['summary']}\n\n"
            
            reply = answer_nl_question(context_prefix + text)
            await update.message.reply_text(reply, disable_web_page_preview=False, reply_to_message_id=update.message.message_id if is_group else None)
            mem_for(chat_id).add(role="assistant", text=reply, user_id=0, username="bot")
        except Exception as e:
            print(f"❌ Legacy processing failed: {e}")
            await update.message.reply_text(
                "I had trouble processing that request. Please try again or use specific commands like /matches, /table, or /live."
            )

async def post_init(application):
    """Post-initialization setup for async components."""
    try:
        if realtime_system:
            await realtime_system.start()
            print("✅ Real-time update system started")
    except Exception as e:
        print(f"⚠️ Real-time system failed to start: {e}")
        print("Bot will continue without real-time features")

def main():
    """Main application setup with enhanced features."""
    print("🚀 Starting Enhanced AI Football Bot...")
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add post-init handler for async components
    app.post_init = post_init
    
    # Add command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("matches", cmd_matches))
    app.add_handler(CommandHandler("lastmatch", cmd_lastmatch))
    app.add_handler(CommandHandler("live", cmd_live))
    app.add_handler(CommandHandler("table", cmd_table))
    app.add_handler(CommandHandler("scorers", cmd_scorers))
    app.add_handler(CommandHandler("form", cmd_form))
    app.add_handler(CommandHandler("lineups", cmd_lineups))
    app.add_handler(CommandHandler("compare", cmd_compare))
    app.add_handler(CommandHandler("compareplayers", cmd_compareplayers))
    app.add_handler(CommandHandler("predict", cmd_predict))
    
    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_router), group=20)
    
    # Add callback query handler for interactive features
    if interactive_handler:
        from telegram.ext import CallbackQueryHandler
        app.add_handler(CallbackQueryHandler(interactive_handler.handle_callback_query))
    
    print("✅ Enhanced AI Football Bot ready!")
    print("🤖 Features enabled:")
    print("   • Multi-step reasoning")
    print("   • Context-aware memory")
    print("   • Dynamic tool selection (49 tools)")
    print("   • Intelligent fallbacks")
    print("   • Proactive suggestions")
    print("   • Weather integration")
    print("   • Enhanced news with sentiment analysis")
    print("   • Currency conversions & market analysis")
    print("   • Performance optimization with caching")
    print("   • Interactive polls and quizzes")
    print("   • Real-time updates and notifications")
    print("   • Advanced personalization")
    print("   • Complex query processing")
    
    # Start the bot
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
