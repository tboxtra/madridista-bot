import os
from typing import Optional
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from orchestrator.brain import answer_nl_question
from orchestrator.tools import (
    tool_next_fixture, tool_last_result, tool_live_now, tool_table, tool_form, tool_scorers,
    tool_next_lineups, tool_compare_teams, tool_compare_players
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

# ---- Command handlers (concise, API-grounded) ----
async def cmd_start(update, context):
    await update.message.reply_text("¡Hala Madrid! Ask me anything football: fixtures, live, lineups, news, player stats, comparisons.")

async def cmd_matches(update, context):
    res = tool_next_fixture({"team_name": " ".join(context.args) if context.args else "Real Madrid"})
    if res.get("ok"):
        await update.message.reply_text(f"{res['when']} • {res['home']} vs {res['away']}")
    else:
        await update.message.reply_text(res.get("message", "No upcoming fixtures."))

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

async def text_router(update, context):
    q = (update.message.text or "").strip()
    reply = answer_nl_question(q)
    await update.message.reply_text(reply, disable_web_page_preview=False)

def main():
    app = Application.builder().token(TOKEN).build()
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
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_router), group=20)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
