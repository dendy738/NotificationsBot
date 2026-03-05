import telebot
from telebot import types, TeleBot
from my_private_config import TOKEN
from datetime import datetime, timedelta
from time import sleep
import json

note_bot = TeleBot(TOKEN)

USERS = {}

@note_bot.message_handler(commands=['start'])
def greet(message):
    chat_id = message.chat.id
    USERS[chat_id] = {}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Start', '/help')
    note_bot.send_message(chat_id, 'Welcome, my friend! I\'m your personal helper for all kinds of events what you will have.'
                                   '\nFor more information about my help for you - push the button "/help"'
                                   '\nFor those who knows how interact with me - click the button "Start"', reply_markup=keyboard)

    def user_info(message):
        USERS[chat_id]['name'] = message.from_user.first_name
        USERS[chat_id]['surname'] = message.from_user.last_name
        USERS[chat_id]['username'] = message.from_user.username


    user_info(message)
    with open('./Data_base.json', 'w', encoding='utf-8') as file:
        js_format = json.dumps(USERS)
        file.write(js_format)



@note_bot.message_handler(commands=['help'])
def help(message):
    chat_id = message.chat.id
    note_bot.send_message(chat_id, 'I was created special for dispatches notifications then you have some events. '
                                   '\nI will send you messages 1 hour, 30 minutes and 15 minutes before your event will start. '
                                   '\nMy sequence of working:'
                                   '\n1. You click button "Start".'
                                   '\n2. You will choose kind of event via buttons.'
                                   '\n3. I will require date and time of your event.'
                                   '\n4. Checking for my notification!😉'
                                   '\nDon\'t forget switch on notifications!')



@note_bot.message_handler(func=lambda message: message.text == 'Start')
def start_work(message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('Job👨‍💻 👩‍💻', 'Visit to a doctor👨‍⚕️ 👩‍⚕️')
    keyboard.row('Birthday🎉 🎊', 'Meeting👥')
    keyboard.row('Study👨‍🎓👩‍🎓', 'Other')
    note_bot.send_message(chat_id, 'Choose your kind of event', reply_markup=keyboard)


user_event = None

#  HANDLE JOBS NOTIFICATIONS
@note_bot.message_handler(func=lambda message: message.text == 'Job👨‍💻 👩‍💻')
def job_notification(message):
    global user_event
    user_event = message.text
    chat_id = message.chat.id
    note_bot.send_message(chat_id, 'Please, send me your date and time in the format DD-MM-YYYY HH:MM'
                                   '\nExactly at this date and time I will remind you about your event.')

    note_bot.register_next_step_handler(message, set_alarm)


#   HANDLE ALARM IF USER HAVE A VISIT TO A DOCTOR
@note_bot.message_handler(func=lambda message: message.text == 'Visit to a doctor👨‍⚕️ 👩‍⚕️')
def doctor_notification(message):
    global user_event
    user_event = message.text
    chat_id = message.chat.id
    note_bot.send_message(chat_id, 'What a doctor do you have?')
    note_bot.register_next_step_handler(message, set_a_doctor)


which_doctor = None

def set_a_doctor(message):
    global which_doctor
    which_doctor = message.text
    note_bot.send_message(message.chat.id, 'Please, send me your date and time in the format DD-MM-YYYY HH:MM'
                                   '\nExactly at this date and time I will remind you about your event.')

    note_bot.register_next_step_handler(message, set_alarm)



#    HANDLE ALARM IF A BIRTHDAY
@note_bot.message_handler(func=lambda message: message.text == 'Birthday🎉 🎊')
def birthday_notification(message):
    global user_event
    user_event = message.text
    note_bot.send_message(message.chat.id, 'Send me who of yours have a birthday')
    note_bot.register_next_step_handler(message, set_a_birthday)


whose_birthday = None

def set_a_birthday(message):
    global whose_birthday
    whose_birthday = message.text
    note_bot.send_message(message.chat.id, 'Please, send me your date and time in the format DD-MM-YYYY HH:MM'
                                   '\nExactly at this date and time I will remind you about your event.')
    note_bot.register_next_step_handler(message, set_alarm)


#    HANDLE ALARM IF HAVE A MEETING
@note_bot.message_handler(func=lambda message: message.text == 'Meeting👥')
def meeting_notification(message):
    global user_event
    user_event = message.text
    note_bot.send_message(message.chat.id, f'Send me a person name whose you had to meeting with')
    note_bot.register_next_step_handler(message, set_a_meeting)


meeting_person = None
def set_a_meeting(message):
    global meeting_person
    meeting_person = message.text
    note_bot.send_message(message.chat.id, 'Please, send me your date and time in the format DD-MM-YYYY HH:MM'
                                           '\nExactly at this date and time I will remind you about your event.')
    note_bot.register_next_step_handler(message, set_alarm)


#    HANDLE ALARM IF HAVE A STUDY
@note_bot.message_handler(func=lambda message: message.text == 'Study👨‍🎓👩‍🎓')
def study_notification(message):
    global user_event
    user_event = message.text
    note_bot.send_message(message.chat.id, 'Please, send me your date and time in the format DD-MM-YYYY HH:MM'
                                           '\nExactly at this date and time I will remind you about your event.')
    note_bot.register_next_step_handler(message, set_alarm)


#    HANDLE ALARM FOR ANY OTHER EVENT
@note_bot.message_handler(func=lambda message: message.text == 'Other')
def other_notification(message):
    global user_event
    user_event = message.text
    note_bot.send_message(message.chat.id, 'Describe your event by 3-4 words.')
    note_bot.register_next_step_handler(message, other_event)

description = None
def other_event(message):
    global description
    description = message.text
    note_bot.send_message(message.chat.id, 'Please, send me your date and time in the format DD-MM-YYYY HH:MM'
                                           '\nExactly at this date and time I will remind you about your event.')
    note_bot.register_next_step_handler(message, set_alarm)



#    GENERAL ALARM FOR EVERY EVENT
def set_alarm(message):
    global user_event, whose_birthday, which_doctor, meeting_person, description
    user_date = datetime.strptime(message.text, '%d-%m-%Y %H:%M') # Date and time which sent user
    # now = datetime.now() # Date and time now
    delta_1_hour = user_date - timedelta(seconds=3600)  # Timedelta obj = 1 hour
    delta_30_minutes = user_date - timedelta(seconds=1800)  # Timedelta obj = 30 minutes
    delta_15_minutes = user_date - timedelta(seconds=900)  # Timedelta obj = 15 minutes

    note_bot.send_message(message.chat.id,
    f'Great! I\'m saved information! Your date and time: {user_date.date()} {user_date.time()}')

    if user_event == 'Job👨‍💻 👩‍💻':
        while True:
            now = datetime.now()
            sleep(2)
            if now.hour == delta_1_hour.hour and now.minute == delta_1_hour.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, your {user_event} will start in an hour!')
                sleep(1680)
            elif now.hour == delta_30_minutes.hour and now.minute == delta_30_minutes.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, your {user_event} will start in an 30 minutes!')
                sleep(780)
            elif now.hour == delta_15_minutes.hour and now.minute == delta_15_minutes.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, your {user_event} will start in a 15 minutes!')
                sleep(780)
            elif now.hour == user_date.hour and now.minute == user_date.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, your {user_event} is started!')
                break

    elif user_event == 'Visit to a doctor👨‍⚕️ 👩‍⚕️':
        while True:
            now = datetime.now()
            sleep(2)
            if now.hour == delta_1_hour.hour and now.minute == delta_1_hour.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, your visit to a {which_doctor} will start in an hour!')
                sleep(1680)
            elif now.hour == delta_30_minutes.hour and now.minute == delta_30_minutes.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, your visit to a {which_doctor} will start in an 30 minutes!')
                sleep(780)
            elif now.hour == delta_15_minutes.hour and now.minute == delta_15_minutes.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, your visit to a {which_doctor} will start in a 15 minutes!')
                sleep(780)
            elif now.hour == user_date.hour and now.minute == user_date.minute:
                note_bot.send_message(message.chat.id, f'{message.from_user.first_name}, your have visit to a {which_doctor} at this moment!')
                break

    elif user_event == 'Birthday🎉 🎊':
        while True:
            now = datetime.now()
            sleep(2)
            if now.hour == user_date.hour and now.minute == user_date.minute:
                note_bot.send_message(message.chat.id,f'{message.from_user.first_name}, your {whose_birthday} have a {user_event}')
                break

    elif user_event == 'Meeting👥':
        while True:
            now = datetime.now()
            sleep(2)
            if now.hour == delta_1_hour.hour and now.minute == delta_1_hour.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, you have a {user_event} with {meeting_person} in an hour!')
                sleep(1680)
            elif now.hour == delta_30_minutes.hour and now.minute == delta_30_minutes.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, you have a {user_event} with {meeting_person}  in an 30 minutes!')
                sleep(780)
            elif now.hour == delta_15_minutes.hour and now.minute == delta_15_minutes.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, you have a {user_event} with {meeting_person}  in a 15 minutes!')
                sleep(780)
            elif now.hour == user_date.hour and now.minute == user_date.minute:
                note_bot.send_message(message.chat.id,
                f'{message.from_user.first_name}, you have a {user_event} with {meeting_person}  at this moment!')
                break

    elif user_event == 'Study👨‍🎓👩‍🎓':
        while True:
            now = datetime.now()
            sleep(2)
            if now.hour == delta_1_hour.hour and now.minute == delta_1_hour.minute:
                note_bot.send_message(message.chat.id,
                                      f'{message.from_user.first_name}, your {user_event} will start in an hour!')
                sleep(1680)
            elif now.hour == delta_30_minutes.hour and now.minute == delta_30_minutes.minute:
                note_bot.send_message(message.chat.id,
                                      f'{message.from_user.first_name}, your {user_event} will start in an 30 minutes!')
                sleep(780)
            elif now.hour == delta_15_minutes.hour and now.minute == delta_15_minutes.minute:
                note_bot.send_message(message.chat.id,
                                      f'{message.from_user.first_name}, your {user_event} will start in a 15 minutes!')
                sleep(780)
            elif now.hour == user_date.hour and now.minute == user_date.minute:
                note_bot.send_message(message.chat.id,
                                      f'{message.from_user.first_name}, your {user_event} is started!')
                break

    elif user_event == 'Other':
        while True:
            now = datetime.now()
            sleep(2)
            if now.hour == delta_1_hour.hour and now.minute == delta_1_hour.minute:
                note_bot.send_message(message.chat.id,
                                      f'{message.from_user.first_name}, your {description} will start in an hour!')
                sleep(1680)
            elif now.hour == delta_30_minutes.hour and now.minute == delta_30_minutes.minute:
                note_bot.send_message(message.chat.id,
                                      f'{message.from_user.first_name}, your {description} will start in an 30 minutes!')
                sleep(780)
            elif now.hour == delta_15_minutes.hour and now.minute == delta_15_minutes.minute:
                note_bot.send_message(message.chat.id,
                                      f'{message.from_user.first_name}, your {description} will start in a 15 minutes!')
                sleep(780)
            elif now.hour == user_date.hour and now.minute == user_date.minute:
                note_bot.send_message(message.chat.id,
                                      f'{message.from_user.first_name}, your event "{description}" is started!')
                break


note_bot.infinity_polling()