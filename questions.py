from clock import get_cooldown_time
import html
from interactions import Client, Intents, listen, slash_command, SlashContext, OptionType, slash_option, ActionRow, Button, ButtonStyle, Guild, Embed, File
import json
import random
import requests
from urllib.parse import urlencode

async def get_questions(amount, difficulty):
    questions_map = {}

    parameters = {}
    parameters['amount'] = amount
    parameters['type'] = "multiple"
    if difficulty is not None:
        parameters['difficulty'] = difficulty

    
    base_url = "https://opentdb.com/api.php?"

    url = base_url + urlencode(parameters)

    response = requests.get(url)
    response_content = json.loads(response.content)

    for idx, result in enumerate(response_content.get('results', []), start=1):
        question = html.unescape(result.get('question', '').strip())
        incorrect_answers = html.unescape(result.get('incorrect_answers'))
        correct_answer = html.unescape(result.get('correct_answer', '').strip())
        category = html.unescape(result.get('category', '').strip())
        difficulty = html.unescape(result.get('difficulty', '').strip().capitalize())
        questions_map[idx] = {
            'question': question,
            'incorrect_answers': incorrect_answers,
            'correct_answer': correct_answer,
            'category': category,
            'difficulty': difficulty
        }

    return questions_map

async def render_question(object, number):
    question = str(object['question'])
    category = object['category']
    difficulty = str(object['difficulty'])
    incorrect_answers = object['incorrect_answers']
    correct_answer = object['correct_answer']

    answer_choices = incorrect_answers + [correct_answer]
    random.shuffle(answer_choices)

    buttons = [
        Button(
            style=1,
            label=f"{chr(ord('A') + index)}",
            custom_id=answer
        )  for index, answer in enumerate(answer_choices)
    ]

    choices_string = "\n"
    for index, answer in enumerate(answer_choices,start=0):
        label = chr(ord('A') + index)
        choices_string += f"{label}. {answer}\n"

    embed = Embed(title=f"Trivia - Question #{number}", description=f"**Category:** {category}\n**Difficulty:** {difficulty}\n\n*{question}*\n{choices_string}\nPlease select the correct answer. Time is up <t:{get_cooldown_time()}:R>")


    return embed, buttons

async def check_answer(questions_map, question_number, answer, score):
    correct_answer = questions_map[question_number]['correct_answer']
    category = questions_map[question_number]['category']
    difficulty = questions_map[question_number]['difficulty']
    question = questions_map[question_number]['question']

    if answer == correct_answer:
        feedback = ":white_check_mark:"
        score += 1
        print(score)
    else:
        feedback = ":x:"

    embed = Embed(title=f"Trivia - Question #{question_number}", description=f"**Category:** {category}\n**Difficulty:** {difficulty.capitalize()}\n\n*{question}*\n\n**Your answer:** {answer}\n**Correct Answer:** {correct_answer}\n\n{feedback}\n\n**Score:** {score}")
    if question_number == len(questions_map):
        end = True
    else:
        end = False
        question_number += 1

    return embed, question_number, score, end
