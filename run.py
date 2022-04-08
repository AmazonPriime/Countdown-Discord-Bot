from datetime import datetime
import os
import asyncio
import json
import re

import discord
import pickle
from discord.ext import commands
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='$')

clock_emojis = {
    '0': '🕛',
    '1': '🕐',
    '2': '🕑',
    '3': '🕒',
    '4': '🕓',
    '5': '🕔',
    '6': '🕕',
    '7': '🕖',
    '8': '🕗',
    '9': '🕘',
    '10': '🕙',
    '11': '🕚',
    '12': '🕛',
    '13': '🕐',
    '14': '🕑',
    '15': '🕒',
    '16': '🕓',
    '17': '🕔',
    '18': '🕕',
    '19': '🕖',
    '20': '🕗',
    '21': '🕘',
    '22': '🕙',
    '23': '🕚',
}

with open("exams.json") as f:
    exam_details = json.load(f)

sad_project_id = 837389562878623764
hacker_bot_spam = 507897269987835935
my_channel_id = 873129698069188638
my_bot_spam = 962014516458192976

chosen_channel = hacker_bot_spam

exam_messages = []
if os.path.exists(os.path.join(os.getcwd(), 'messages.pickle')):
    with open('messages.pickle', 'rb') as f:
        exam_messages = pickle.load(f)

date_regex = re.compile(r'\d+\/\d+\/\d+ \d+:\d+')
name_regex = re.compile(r'^\s*(.*?)\|')


def format_exam(exam, update=False):
    name = exam.get('course_name')
    if not update:
        date = datetime.strptime(exam.get('datetime'), "%Y-%m-%d %H:%M:%S")
    else:
        date = datetime.strptime(exam.get('datetime'), "%d/%m/%Y %H:%M:%S")
    date_str = date.strftime("%d/%m/%Y %H:%M")
    today = datetime.today()
    mins = int((date - today).total_seconds() / 60)
    if mins > 0:
        msg = f'{name.ljust(30)} | {date_str} | {str(int(mins / 60)).rjust(3)} hours'
        return msg + f' | {str(mins).rjust(5)} mins'
    return ''


async def exams():
    if len(exam_messages) > 0:
        return

    channel = client.get_channel(chosen_channel)

    init_msg = 'Countdown to each (H) and (M) exam - updates every minute.'
    init_msg += '\nIf any are missing let me know <@215227555035349004>'

    await channel.send(init_msg)

    msgs = []
    msg = '```css\n'
    count = 0
    for exam in exam_details:
        exam_msg = format_exam(exam)
        if len(exam_msg) > 0:
            msg += exam_msg
            msg += '\n'
            count += 1

        if (count + 1) % 20 == 0:
            msgs.append(msg + '```')
            msg = '```css\n'

    for m in msgs:
        sent_msg = await channel.send(m)
        exam_messages.append(sent_msg.id)

    with open('messages.pickle', 'wb') as f:
        pickle.dump(exam_messages, f)


async def update_message(channel, id):
    message = await channel.fetch_message(id)
    lines = message.content.split('\n')
    new_lines = ['```css']
    for line in lines[1:-1]:
        name = re.search(name_regex, line).group(1).strip()
        date_str = re.search(date_regex, line).group()
        exam = {
            'course_name': name,
            'datetime': date_str + ':00',
        }
        new_lines.append(format_exam(exam, update=True))
    new_lines.append('```')
    await message.edit(content="\n".join(new_lines))
    print(f'{datetime.today()} updated message with id "{id}"')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    # update nickname on all servers
    for guild in client.guilds:
        nickname = '#bot-commands!'
        await guild.me.edit(nick=nickname)

    await exams()

    scheduler = AsyncIOScheduler()

    channel = client.get_channel(chosen_channel)
    for msg in exam_messages:
        cron = CronTrigger(minute='0-59', end_date="2022-05-30 16:00:00")
        scheduler.add_job(update_message, cron, args=[channel, msg])

    scheduler.start()


client.run(TOKEN)
