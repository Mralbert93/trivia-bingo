import asyncio
from interactions import Client, Intents, listen, slash_command, SlashContext, OptionType, slash_option, ActionRow, Button, ButtonStyle, Guild, Embed, File
from interactions.api.events import Component
import os
from questions import get_questions, render_question, check_answer

token= os.environ.get("DISCORD_TOKEN")

bot = Client(intents=Intents.DEFAULT)

active_game = False
score = 0
questions_map = {}

@slash_command(
        name="trivia",
        sub_cmd_name="start",
        sub_cmd_description="Start a trivia game",
)
@slash_option(
    name="amount",
    description="Amount of questions",
    required=True,
    opt_type=OptionType.INTEGER
)
@slash_option(
    name="difficulty",
    description="Difficulty of questions (easy, medium, hard)",
    required=False,
    opt_type=OptionType.STRING
)
async def start(ctx: SlashContext, amount: int, difficulty: str = None):
    global active_game
    global questions_map
    global question_number

    if active_game == True:
        await ctx.send(f"{ctx.author.mention}, sorry a game is already running. Only one game can be run at a time.", ephemeral=True)
        return

    questions_map = await get_questions(amount, difficulty)
    question_number = 1
    active_game = True

    if difficulty is None:
        difficulty = "Random"

    embed = Embed(title="Trivia", description=f"Trivia game ready to start!\n\n**Questions:** {len(questions_map)}\n**Difficulty:** {difficulty.capitalize()}\n\nGood luck!")
    start_button = Button(label="Start", custom_id="start_button", style=ButtonStyle.GREEN)

    await ctx.send(embeds=embed,components=[start_button])

@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx
    global active_game
    global questions_map
    global question_number
    global score

    match ctx.custom_id:
        case "start_button":
            embed, buttons = await render_question(questions_map[1],1)
            post = await ctx.edit_origin(embeds=embed,components=[buttons])
            await asyncio.sleep(15)
            if active_game == True:
                if question_number == 1:
                    embed, question_number, score, end = await check_answer(questions_map, question_number, None, score)
                    next_button = Button(label="Next", custom_id="next_button", style=ButtonStyle.GREEN)
                    await post.edit(embeds=embed,components=[next_button])
        case "next_button":
            embed, buttons = await render_question(questions_map[question_number], question_number)
            original_question_number = question_number
            post = await ctx.edit_origin(embeds=embed,components=[buttons])
            await asyncio.sleep(15)
            if original_question_number == question_number:
                embed, question_number, score, end = await check_answer(questions_map, question_number, None, score)
                if end == False:
                    next_button = Button(label="Next", custom_id="next_button", style=ButtonStyle.GREEN)
                    await post.edit(embeds=embed,components=[next_button])
                else:
                    await post.edit(embeds=embed,components=[])
                    active_game = False
                    score = 0
        case _:
            embed, question_number, score, end = await check_answer(questions_map, question_number, ctx.custom_id, score)
            if end == False:
                next_button = Button(label="Next", custom_id="next_button", style=ButtonStyle.GREEN)
                await ctx.edit_origin(embeds=embed,components=[next_button])
            else:
                await ctx.edit_origin(embeds=embed,components=[])
                active_game = False
                score = 0

@listen
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Start bot
bot.start(token)
