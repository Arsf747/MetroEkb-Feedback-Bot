import httplib2 
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import telebot
from telebot import types
from settings import token, devid, spreadsheetId
import random
# УСТАНОВИТЕ СЛЕДУЮЩИЕ БИБЛИОТЕКИ ЧЕРЕЗ PIP INSTALL:
# pip install httplib2
# pip install google-api-python-client
# pip install oauth2client
# pip install telebot

bot = telebot.TeleBot(token)

CREDENTIALS_FILE = 'e:\Desktop\ebot-metroekb-feedback\sacred-flash-447616-b7-7fad4494fd76.json' # Создайте сервисный аккаунт для использования google sheets, затем замените на реальный путь к файлу с похожим названием
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)
driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth)
strek = 2
while True:
        ranges = [f"Reviews!A{strek}:D{strek}"]
        results = service.spreadsheets().values().batchGet(spreadsheetId = spreadsheetId, 
                                            ranges = ranges, 
                                            valueRenderOption = 'UNFORMATTED_VALUE',  
                                            dateTimeRenderOption = 'FORMATTED_STRING').execute() 
        if 'values' not in results['valueRanges'][0]:
            last_full_str = strek - 1
            break
        else:
            strek += 1
print(last_full_str)

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.username
    user_fname = message.from_user.first_name
    user_sname = message.from_user.last_name
    if not user_name:
        if not user_sname:
            full_user_name = f'{user_fname}'
        else:
            full_user_name = f'{user_fname} {user_sname}'
    else:
        if not user_sname:
            full_user_name = f'@{user_name} ({user_fname})'
        else:
            full_user_name = f'@{user_name} ({user_fname} {user_sname})'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Написать отзыв")
    btn2 = types.KeyboardButton("Прочитать случайный отзыв")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Здравствуйте, это бот с отзывами о симуляторе метро Екатеринбурга в Roblox. Напишите отзыв или посмотрите случайный отзыв"
                                       "\nСсылки"
                                       "\nИгра: https://www.roblox.com/games/9808123850"
                                       "\nRoblox-группа: https://www.roblox.com/communities/34159783/Yekaterinburg-Subway-Group"
                                       "\nDiscord-сервер: https://discord.gg/5gcMmGb4Qa"
                                       "\nTelegram-канал: https://t.me/metroekbsimulator", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: next_action(msg, full_user_name))
def next_action(message, full_user_name):
    act = message.text
    if act == "Написать отзыв":
        bot.send_message(message.chat.id, "Напишите, что думаете об игре: что вам бы хотелось добавить/убрать? Может сообщить о баге?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, lambda msg: review_insert(msg, full_user_name))
    elif act == "Прочитать случайный отзыв":
        stroke = random.randint(2,last_full_str)
        ranges = [f"Reviews!A{stroke}:D{stroke}"]
        results = service.spreadsheets().values().batchGet(spreadsheetId = spreadsheetId, 
                                            ranges = ranges, 
                                            valueRenderOption = 'UNFORMATTED_VALUE',  
                                            dateTimeRenderOption = 'FORMATTED_STRING').execute() 
        sheet_values = results['valueRanges'][0]['values']
        bot.send_message(message.chat.id, f"Отзыв от {sheet_values[0][2]}, написан {str(sheet_values[0][1])[:16]}"
                         f"\n{sheet_values[0][3]}", reply_markup=types.ReplyKeyboardRemove())

def review_insert(message, full_user_name):
    review = message.text
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Спасибо за отзыв!")
    date = datetime.now()
    strok = 2
    while True:
        ranges = [f"Reviews!A{strok}:D{strok}"]
        results = service.spreadsheets().values().batchGet(spreadsheetId = spreadsheetId, 
                                            ranges = ranges, 
                                            valueRenderOption = 'UNFORMATTED_VALUE',  
                                            dateTimeRenderOption = 'FORMATTED_STRING').execute() 
        if 'values' not in results['valueRanges'][0]:
            service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = {
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"Reviews!A{strok}:D{strok}",
                "majorDimension": "ROWS",
                "values": [
                            [user_id, str(date), full_user_name, review],
                        ]}
            ]
            }).execute()
            last_full_str = strok
            bot.send_message(devid, f"Новый отзыв от {full_user_name}! Иди читай!!!")
            break
        else:
            strok += 1
    
bot.polling()