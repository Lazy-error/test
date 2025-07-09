# Basic telegram bot for gym training
import logging
import sqlite3
from datetime import datetime
from telegram import Update
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
    weight REAL,
    reps INTEGER,
    rest REAL,
    FOREIGN KEY(exercise_id) REFERENCES exercises(id)
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS workouts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    datetime TEXT,
    notified INTEGER DEFAULT 0
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS workout_exercises(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER,
    exercise_id INTEGER,
    FOREIGN KEY(workout_id) REFERENCES workouts(id),
    FOREIGN KEY(exercise_id) REFERENCES exercises(id)
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS workout_sets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_exercise_id INTEGER,
    weight REAL,
    reps INTEGER,
    rest REAL,
    FOREIGN KEY(workout_exercise_id) REFERENCES workout_exercises(id)
)''')

db.commit()

(NEW_EXERCISE_NAME, NEW_EXERCISE_SET) = range(2)
(NEW_WORKOUT_DATETIME, NEW_WORKOUT_EXERCISE, NEW_WORKOUT_SET) = range(3)

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
            weight_str, reps_str, rest_str = text.split()
            weight = float(weight_str)
            reps = int(reps_str)
            rest = float(rest_str)
            user_data_temp_sets[update.effective_user.id].append({'weight': weight, 'reps': reps, 'rest': rest})
            update.message.reply_text('Добавлено. Введите следующий сет или "done":')
        except ValueError:
            update.message.reply_text('Неверный формат. Введите три числа через пробел.')
        return NEW_EXERCISE_SET

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Действие отменено.')
    return ConversationHandler.END

def new_workout_start(update: Update, context: CallbackContext):
    update.message.reply_text('Введите дату и время тренировки в формате ГГГГ-ММ-ДД ЧЧ:ММ:')
    return NEW_WORKOUT_DATETIME


def new_workout_datetime(update: Update, context: CallbackContext):
    dt_str = update.message.text
    try:
        datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
    except ValueError:
        update.message.reply_text('Неверный формат. Попробуйте ещё раз:')
        return NEW_WORKOUT_DATETIME
    context.user_data['workout_datetime'] = dt_str
    context.user_data['workout_exercises'] = []
    exercises = cur.execute('SELECT id, name FROM exercises').fetchall()
    if not exercises:
        update.message.reply_text('Нет доступных упражнений. Сначала создайте их.')
        return ConversationHandler.END
    text = 'Введите id упражнения или "done" для завершения:\n'
    text += '\n'.join(f"{e[0]}: {e[1]}" for e in exercises)
    update.message.reply_text(text)
    return NEW_WORKOUT_EXERCISE

def new_workout_exercise(update: Update, context: CallbackContext):
    text = update.message.text
    if text.lower() == 'done':
        if not context.user_data['workout_exercises']:
            update.message.reply_text('Нужно добавить хотя бы одно упражнение.')
            return NEW_WORKOUT_EXERCISE
        # save workout
        cur.execute('INSERT INTO workouts(user_id, datetime) VALUES (?,?)', (update.effective_user.id, context.user_data['workout_datetime']))
        workout_id = cur.lastrowid
        for ex in context.user_data['workout_exercises']:
            cur.execute('INSERT INTO workout_exercises(workout_id, exercise_id) VALUES (?,?)', (workout_id, ex['exercise_id']))
            w_ex_id = cur.lastrowid
            for s in ex['sets']:
                cur.execute('INSERT INTO workout_sets(workout_exercise_id, weight, reps, rest) VALUES (?,?,?,?)', (w_ex_id, s['weight'], s['reps'], s['rest']))
        db.commit()
        update.message.reply_text('Тренировка создана.')
        return ConversationHandler.END
    else:
        try:
            ex_id = int(text)
            ex = cur.execute('SELECT id FROM exercises WHERE id=?', (ex_id,)).fetchone()
            if not ex:
                update.message.reply_text('Неверный id. Попробуйте ещё раз:')
                return NEW_WORKOUT_EXERCISE
            context.user_data['current_exercise'] = ex_id
            context.user_data['current_sets'] = []
            update.message.reply_text('Введите параметры сета в формате "вес повторения отдых" или "done" для завершения упражнения:')
            return NEW_WORKOUT_SET
        except ValueError:
            update.message.reply_text('Введите число или "done":')
            return NEW_WORKOUT_EXERCISE

def new_workout_set(update: Update, context: CallbackContext):
    text = update.message.text
    if text.lower() == 'done':
        if not context.user_data['current_sets']:
            update.message.reply_text('Добавьте хотя бы один сет или отмените упражнение:')
            return NEW_WORKOUT_SET
        context.user_data['workout_exercises'].append({
            'exercise_id': context.user_data['current_exercise'],
            'sets': context.user_data['current_sets']
        })
        exercises = cur.execute('SELECT id, name FROM exercises').fetchall()
        text = 'Введите id следующего упражнения или "done" для завершения:\n'
        text += '\n'.join(f"{e[0]}: {e[1]}" for e in exercises)
        update.message.reply_text(text)
        return NEW_WORKOUT_EXERCISE
    else:
        try:
            weight_str, reps_str, rest_str = text.split()
            weight = float(weight_str)
            reps = int(reps_str)
            rest = float(rest_str)
            context.user_data['current_sets'].append({'weight': weight, 'reps': reps, 'rest': rest})
            update.message.reply_text('Сет добавлен. Введите следующий или "done":')
        except ValueError:
            update.message.reply_text('Неверный формат. Введите "вес повторения отдых" или "done":')
        return NEW_WORKOUT_SET


def check_workouts(context: CallbackContext):
    now = datetime.now()
    rows = cur.execute('SELECT id, user_id, datetime FROM workouts WHERE notified=0').fetchall()
    for w in rows:
        try:
            workout_time = datetime.strptime(w[2], '%Y-%m-%d %H:%M')
        except ValueError:
            continue
        if now >= workout_time:
            context.bot.send_message(chat_id=w[1], text=f'Напоминание о тренировке {w[2]}!')
            cur.execute('UPDATE workouts SET notified=1 WHERE id=?', (w[0],))
    db.commit()

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
            NEW_WORKOUT_DATETIME: [MessageHandler(Filters.text & ~Filters.command, new_workout_datetime)],
            NEW_WORKOUT_EXERCISE: [MessageHandler(Filters.text & ~Filters.command, new_workout_exercise)],
            NEW_WORKOUT_SET: [MessageHandler(Filters.text & ~Filters.command, new_workout_set)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(ex_conv)
    dp.add_handler(workout_conv)

    job_queue: JobQueue = updater.job_queue
    job_queue.run_repeating(check_workouts, interval=60, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    import os
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        print('Please set TELEGRAM_TOKEN environment variable')
    else:
        main(token)
