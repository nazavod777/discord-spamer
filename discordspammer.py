import threading
import requests
from random import choice, randint
from time import sleep
from threading import Thread
from json import loads
from os import system
from ctypes import windll
from sys import stderr
from loguru import logger
from urllib3 import disable_warnings
from telebot import TeleBot
from telebot import apihelper

disable_warnings()
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <level>{message}</level>")
clear = lambda: system('cls')
print('Telegram Channel - https://t.me/n4z4v0d & https://t.me/earlyberkut\n')
windll.kernel32.SetConsoleTitleW('Discord Bot | by NAZAVOD&EARLY BERKUT')
lock = threading.Lock() 

tokensfolder = str(input('TXT файл с токенами Discord: '))
with open(tokensfolder, 'r', encoding='utf-8') as file:
    data = [token.strip() for token in file]

if ':' not in data[0]:
    chat_id = int(input('Введите ChatID Discord: '))
else:
    chat_id = 0

use_telegram = str(input('Оповещать вас в Telegram при ответах на ваши сообщения и упоминании вас (y/N): '))

if use_telegram in ('y', 'Y'):
    bot_token = str(input('Введите токен бота Telegram: '))
    bot = TeleBot(bot_token)
    #bot.config['api_key'] = bot_token

    tg_user_id = int(input('Введите ваш UserID TG: '))

    useproxy_telegram = str(input('Использовать proxy для Telegram? (y/N): '))
    if useproxy_telegram in ('y', 'Y'):
        proxy_type_telegram = str(input('Введите тип proxy для Telegram (https/socks4/socks5): '))
        proxy_str_telegram = str(input('Введите proxy для Telegram (ip:port or use:pass@ip:port: )'))
        apihelper.proxy = {'https':f'{proxy_type_telegram}://{proxy_str_telegram}'}


take_msgs = int(input('Как брать сообщения из TXT? 1 - по порядку, 2 - рандомно: '))

msg_input_method = int(input('Как грузить TXT с сообщениями: 1. общий TXT для каждого аккаунта; 2 - к каждому токену свой TXT: '))

if msg_input_method == 1:
    current_msg_folder = str(input('TXT файл с сообщениями: '))
else:
    msg_folders = {}
    for every_token in data:
        if ':' not in data[0]:
            msg_folders[str(every_token)] = str(input(f'Перетяните файл с сообщениями для {every_token}: '))
        else:
            msg_folders[str(every_token)] = str(input('Перетяните файл с сообщениями для '+every_token.split(':')[0]+': '))

delete_message_after_send = str(input('Удалять сообщение после отправки? (y/N): '))

if delete_message_after_send in ('y', 'Y'):
    sleep_before_delete_msg = int(input('Время сна перед удалением сообщения после отправки: '))

useproxy = str(input('Использовать proxy? (y/N) !! не проверено !!: '))
if useproxy in ('y', 'Y'):
    proxytype = str(input('Введите тип proxy (http/https/socks4/socks5): '))
    proxyfolder = str(input('Перетяните файл с proxy: '))

fist_msg_delay_type = input('Задержка перед отправкой ПЕРВОГО сообщения. Целое число, либо диапазон (example: 0-20, or 50): ')
if '-' in fist_msg_delay_type:
    delayrange_firstmsg = fist_msg_delay_type.split('-')

every_msg_delay_type = input('Задержка перед отправкой последующих сообщений. Целое число, либо диапазон (example: 0-20, or 50): ')
if '-' in every_msg_delay_type:
    delayrange_everymsg = every_msg_delay_type.split('-')

sleep_when_typing = input('Время имитации печатания. Целое число, либо диапазон (example: 0-20, or 50): ')
if '-' in sleep_when_typing:
    range_typing_msg = sleep_when_typing.split('-')

msg_set = []
proxies_list = []
def rand_msg(current_msg_folder):
    global msg_set
    if 'msg_set' not in globals() or len(msg_set) < 1:
        msg_set = open(current_msg_folder, 'r', encoding='utf-8').read().splitlines()
    if take_msgs == 1:
        taked_msg = msg_set.pop(0)
    else:
        taked_msg = msg_set.pop(randint(0, len(msg_set)-1))
    return(taked_msg)

def getproxy():
    global proxies_list
    if 'proxies_list' not in globals() or len(proxies_list) < 1:
        proxies_list = open(proxyfolder, 'r', encoding='utf-8').read().splitlines()
    return(proxies_list.pop(0))

def check_tags(session, chat_id, ds_user_id, bot, username, token):
    last_id = None
    msg_ids = []
    all_ids = []
    while True:
        try:
            r = session.get(f'https://discord.com/api/v9/channels/{chat_id}/messages?limit=100')
            if 'retry_after' in loads(r.text):
                errortext = loads(r.text)['message']
                timetosleep = loads(r.text)['retry_after']
                logger.error(f'Error: {errortext}, sleeping {timetosleep}')
                sleep(timetosleep)
                r = session.get(f'https://discord.com/api/v9/channels/{chat_id}/messages?limit=100')
            for every_msg_id in loads(r.text):
                all_ids.append(every_msg_id['id'])
            if last_id not in all_ids:
                all_ids = []
                msg_ids = []
            if r.status_code == 200 and len(loads(r.text)) > 0:
                for usermessage in loads(r.text):
                    current_id = usermessage['id']
                    # <-- check replies
                    if 'referenced_message' in usermessage:
                        if str(ds_user_id) == str(usermessage['referenced_message']['author']['id']) and current_id not in msg_ids:
                            reply_content = usermessage['content']

                            logger.success(f'[{username}] ваше сообщение переслали в ChatID: {chat_id}')
                            msg_ids.append(current_id)

                            bot_msg_resp = str(bot.send_message(int(tg_user_id), f'Ваше сообещние переслали\nChatID: {chat_id}\nUsername: {username}\nToken: {token}\nMsg id: {current_id}\nMsg text: {reply_content}'))
                            if 'from_user' in bot_msg_resp:
                                logger.success(f'Сообщение в Telegram успешно отправлено')
                            else:
                                logger.error(f'Ошибка при отправке сообщения в Telegram: {bot_msg_resp}')
                    # --> check replies

                    # <-- check tags
                    current_message = str(usermessage['content']).replace('\n', '').replace('\r', '')
                    if f'<@!{str(ds_user_id)}>' in current_message and current_id not in msg_ids:
                        logger.success(f'[{username}] вас упомянули в ChatID: {chat_id}')
                        msg_ids.append(current_id)
                        bot_msg_resp = str(bot.send_message(int(tg_user_id), f'Вас упомянули\nChatID: {chat_id}\nUsername: {username}\nToken: {token}\nMsg id: {current_id}\nMsg text: {current_message}'))
                        if 'from_user' in bot_msg_resp:
                            logger.success(f'Сообщение в Telegram успешно отправлено')
                        else:
                            logger.error(f'Ошибка при отправке сообщения в Telegram: {bot_msg_resp}')
                    # --> check tags
                    last_id = current_id
        except Exception as error:
            logger.error(f'[{username}] ошибка при парсе сообщений для проверки упомянаний: {str(error)}')
            continue


def mainth(token, first_start, chat_id, succinit, current_msg_folder):
    if first_start == True:
        try:
            if '-' in fist_msg_delay_type:
                first_start_sleeping = randint(int(delayrange_firstmsg[0]), int(delayrange_firstmsg[1]))
            else:
                first_start_sleeping = fist_msg_delay_type
            if ':' in token:
                chat_id = token.split(':')[1]
                token = token.split(':')[0]
            session = requests.Session()
            session.headers['authorization'] = token
            if useproxy in ('y', 'Y'):
                lock.acquire()
                proxystr = getproxy()
                lock.release()
                session.proxies.update({'http': f'{proxytype}://{proxystr}', 'https': f'{proxytype}://{proxystr}'})
            r = session.get('https://discordapp.com/api/users/@me', verify=False)
            if 'username' not in loads(r.text):
                raise Exception('invalidtoken')
            username = loads(r.text)['username']
            ds_user_id = loads(r.text)['id']
            if use_telegram in ('y', 'Y'):
                Thread(target=check_tags, args=(session, chat_id, ds_user_id, bot, username, token,)).start()
            logger.info(f'Первый запуск для [{username}], сплю {str(first_start_sleeping)} секунд перед первым сообщением')
            sleep(int(first_start_sleeping))
        except Exception as error:
            if str(error) == 'invalidtoken':
                logger.error(f'Токен [{token}] невалидный')
            else:
                logger.error(f'Ошибка при первоначальной настройке для [{token}]: {str(error)}')
            succinit = False
        else:
            succinit = True
    while succinit == True:
        first_start = False
        try:
            while True:
                lock.acquire()
                random_message = str(rand_msg(current_msg_folder))
                lock.release()
                json_data = {'content': str(random_message), 'tts': False}
                r = session.post(f'https://discord.com/api/v9/channels/{chat_id}/typing', verify=False)

                if '-' in sleep_when_typing:
                    time_sleep_typing = int(randint(int(range_typing_msg[0]), int(range_typing_msg[1])))
                else:
                    time_sleep_typing = int(sleep_when_typing)
                logger.info(f'Имитирую печатание сообщения для [{username}] в течение {time_sleep_typing} сек')
                sleep(time_sleep_typing)
                r = session.post(
                    f'https://discord.com/api/v9/channels/{chat_id}/messages', json=json_data, verify=False)
                if 'id' in loads(r.text):
                    message_id = str(loads(r.text)['id'])
                    logger.success(f'Сообщение [{random_message}] от [{username}] успешно отправлено')
                    break
                elif 'message' in loads(r.text):
                    errormsg = loads(r.text)['message']
                    if 'retry_after' in loads(r.text):
                        timesleep = float(loads(r.text)['retry_after'])
                        logger.error(f'Ошибка: {errormsg} для [{username}], сплю {str(timesleep)} секунд')
                        sleep(timesleep)
                    elif errormsg == 'Missing Access':
                        raise Exception('erroraccess')
                    else:
                        raise Exception(errormsg)


            if delete_message_after_send in ('y', 'Y'):
                for i in range(10):
                    logger.info(f'Сплю {sleep_before_delete_msg} перед удалением сообщения')
                    sleep(sleep_before_delete_msg)
                    r = session.delete(f'https://discord.com/api/v9/channels/{chat_id}/messages/{message_id}', verify=False)
                    if r.status_code == 204:
                        logger.success(f'Сообщение с ID {message_id} и содержимым [{random_message}] от [{username}] успешно удалено')
                        break
                    elif 'retry_after' in loads(r.text):
                        timesleep = float(loads(r.text)['retry_after'])
                        logger.error(f'Ошибка: {errormsg} для [{username}], сплю {str(timesleep)} секунд')
                        sleep(timesleep)
                    else:
                        logger.error(f'Не удалось удалить сообщение для [{username}], статус ответа: {str(r.status_code)}, содержимое ответа: {str(r.text)}')
                        sleep(3)
            if '-' in every_msg_delay_type:
                time_to_sleep_everymsg = int(randint(int(delayrange_everymsg[0]), int(delayrange_everymsg[1])))
            else:
                time_to_sleep_everymsg = int(every_msg_delay_type)
            logger.info (f'Сплю {str(time_to_sleep_everymsg)} секунд для [{username}]')
            sleep(int(time_to_sleep_everymsg))

        except Exception as error:
            if str(error) == 'erroraccess':
                logger.error(f'Вы не можете отправлять сообщения в канале, выключаю поток для [{username}]')
                succinit = False
                break
            else:
                logger.error(f'Ошибка для [{username}]: {str(error)}')
                pass

clear()
for _ in range(len(data)):
    while data:
        current_token = data.pop(0)
        if msg_input_method != 1:
            current_msg_folder = msg_folders[str(current_token)]
        Thread(target=mainth, args=(current_token, True, chat_id, False, current_msg_folder)).start()
