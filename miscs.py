import secrets
import string
import datetime
import json


def generate_random_password(length=15):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def current_time():
    return datetime.datetime.now()


def convert_datetime_in_feed(time):
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    month_idx = time.month - 1
    return time.strftime("%d {} %Y %H:%M").format(months[month_idx])


def convert_datetime_in_chat(time):
    return time.strftime("%d.%m.%Y %H:%M:%S")


def convert_comments_to_json(comments):
    comments_list = []

    for comment in comments:
        comments_list.append({
            'username': comment[0],
            'avatar': comment[1],
            'content': comment[2],
            'timestamp': convert_datetime_in_feed(comment[3])
        })

    return comments_list


def process_notes(db, notes, user_id):
    for note in notes:
        note['is_liked'] = db.has_like(user_id, note['note_id'])
        note['is_favorited'] = db.has_favorite(user_id, note['note_id'])

        if note['type'] == 'post':
            note.update(db.get_post_info(note['note_id']))

        elif note['type'] == 'recipe':
            recipe_data = db.get_recipe_info(note['note_id'])
            recipe_data['ingredients'] = json.loads(recipe_data['ingredients'])
            recipe_data['steps'] = json.loads(recipe_data['steps'])
            note.update(recipe_data)

        elif note['type'] == 'video_recipe':
            video_recipe_data = db.get_video_recipe_info(note['note_id'])
            note.update(video_recipe_data)

    return notes


def process_recipe(recipe_form):
    ingredients = []
    steps = []

    ingredient_names = recipe_form.getlist('ingredient_name')
    ingredient_amounts = recipe_form.getlist('ingredient_amount')

    step_titles = recipe_form.getlist('step_title')
    step_time_amounts = recipe_form.getlist('timeAmount')
    step_time_units = recipe_form.getlist('unit_text')
    step_durations = [f'{num} {unit}' for num,
                      unit in zip(step_time_amounts, step_time_units)]
    step_descriptions = recipe_form.getlist('step_description')

    for name, amount in zip(ingredient_names, ingredient_amounts):
        ingredients.append({'name': name, 'amount': amount})

    for title, duration, description in zip(step_titles, step_durations,
                                            step_descriptions):
        steps.append({'title': title, 'duration': duration,
                      'description': description})

    ingredients_json = json.dumps(ingredients)
    steps_json = json.dumps(steps)

    return ingredients_json, steps_json
