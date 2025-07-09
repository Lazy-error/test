# Basic telegram bot for gym training
import logging
import sqlite3
from datetime import datetime, date
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, JobQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = sqlite3.connect('gym.db', check_same_thread=False)
cur = db.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS exercises(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS sets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER,
    weight INTEGER,
    reps INTEGER,
    rest INTEGER,
    FOREIGN KEY(exercise_id) REFERENCES exercises(id)
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS workouts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS workout_exercises(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER,
    exercise_id INTEGER,
    FOREIGN KEY(workout_id) REFERENCES workouts(id),
    FOREIGN KEY(exercise_id) REFERENCES exercises(id)
)''')

db.commit()

(NEW_EXERCISE_NAME, NEW_EXERCISE_SET) = range(2)
(NEW_WORKOUT_DATE, NEW_WORKOUT_EXERCISES) = range(2)

user_data_temp_sets = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Используй /newexercise для создания упражнения и /newworkout для создания тренировки.')


def new_exercise_start(update: Update, context: CallbackContext):
    update.message.reply_text('Введите название упражнения:')
    return NEW_EXERCISE_NAME

def new_exercise_name(update: Update, context: CallbackContext):
    context.user_data['exercise_name'] = update.message.text
    update.message.reply_text('Введите параметры сета в формате "вес повторения отдых" или "done" для завершения:')
    user_data_temp_sets[update.effective_user.id] = []
    return NEW_EXERCISE_SET

def new_exercise_set(update: Update, context: CallbackContext):
    text = update.message.text
    if text.lower() == 'done':
        name = context.user_data['exercise_name']
        cur.execute('INSERT INTO exercises(name) VALUES (?)', (name,))
        ex_id = cur.lastrowid
        for s in user_data_temp_sets[update.effective_user.id]:
            cur.execute('INSERT INTO sets(exercise_id, weight, reps, rest) VALUES (?,?,?,?)', (ex_id, s['weight'], s['reps'], s['rest']))
        db.commit()
        update.message.reply_text(f'Упражнение "{name}" создано.')
        return ConversationHandler.END
    else:
        try:
            weight, reps, rest = map(int, text.split())
            user_data_temp_sets[update.effective_user.id].append({'weight': weight, 'reps': reps, 'rest': rest})
            update.message.reply_text('Добавлено. Введите следующий сет или "done":')
        except ValueError:
            update.message.reply_text('Неверный формат. Введите три числа через пробел.')
        return NEW_EXERCISE_SET

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Действие отменено.')
    return ConversationHandler.END

def new_workout_start(update: Update, context: CallbackContext):
    update.message.reply_text('Введите дату тренировки в формате ГГГГ-ММ-ДД:')
    return NEW_WORKOUT_DATE


def new_workout_date(update: Update, context: CallbackContext):
    context.user_data['workout_date'] = update.message.text
    exercises = cur.execute('SELECT id, name FROM exercises').fetchall()
    if not exercises:
        update.message.reply_text('Нет доступных упражнений. Сначала создайте их.')
        return ConversationHandler.END
    text = 'Выберите id упражнений через пробел:\n'
    text += '\n'.join(f"{e[0]}: {e[1]}" for e in exercises)
    update.message.reply_text(text)
    return NEW_WORKOUT_EXERCISES

def new_workout_exercises(update: Update, context: CallbackContext):
    ids = update.message.text.split()
    workout_date = context.user_data['workout_date']
    cur.execute('INSERT INTO workouts(user_id, date) VALUES (?,?)', (update.effective_user.id, workout_date))
    workout_id = cur.lastrowid
    for ex_id in ids:
        cur.execute('INSERT INTO workout_exercises(workout_id, exercise_id) VALUES (?,?)', (workout_id, ex_id))
    db.commit()
    update.message.reply_text('Тренировка создана.')
    return ConversationHandler.END


def check_workouts(context: CallbackContext):
    today = date.today().isoformat()
    rows = cur.execute('SELECT id, user_id, date FROM workouts WHERE date=?', (today,)).fetchall()
    for w in rows:
        context.bot.send_message(chat_id=w[1], text=f'Напоминание о тренировке сегодня ({w[2]})!')

def main(token):
    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    ex_conv = ConversationHandler(
        entry_points=[CommandHandler('newexercise', new_exercise_start)],
        states={
            NEW_EXERCISE_NAME: [MessageHandler(Filters.text & ~Filters.command, new_exercise_name)],
            NEW_EXERCISE_SET: [MessageHandler(Filters.text & ~Filters.command, new_exercise_set)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    workout_conv = ConversationHandler(
        entry_points=[CommandHandler('newworkout', new_workout_start)],
        states={
            NEW_WORKOUT_DATE: [MessageHandler(Filters.text & ~Filters.command, new_workout_date)],
            NEW_WORKOUT_EXERCISES: [MessageHandler(Filters.text & ~Filters.command, new_workout_exercises)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(ex_conv)
    dp.add_handler(workout_conv)

    job_queue: JobQueue = updater.job_queue
    job_queue.run_repeating(check_workouts, interval=3600, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    import os
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        print('Please set TELEGRAM_TOKEN environment variable')
    else:
        main(token)
