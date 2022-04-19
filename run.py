from datetime import datetime, timedelta
import os
import json
import re
import random

import pickle
import discord
from discord.ext import commands
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='$')

with open("exams.json") as f:
    exam_details = json.load(f)

exam_memes = os.listdir(os.path.join(os.getcwd(), 'exam_memes'))
finished_memes = os.listdir(os.path.join(os.getcwd(), 'times_up'))

sad_project_id = 837389562878623764
hacker_bot_spam = 507897269987835935
hackerman_gen = 492008434309398539
pure_dread_id = 964625015419056128

my_channel_id = 873129698069188638
my_bot_spam = 962014516458192976

chosen_channel = my_bot_spam
general_channel = my_channel_id

exam_messages = []
if os.path.exists(os.path.join(os.getcwd(), 'messages.pickle')):
    with open('messages.pickle', 'rb') as f:
        exam_messages = pickle.load(f)

date_regex = re.compile(r'\d+\/\d+\/\d+ \d+:\d+')
name_regex = re.compile(r'^\s*(.*?)\|')
# name_regex = re.compile(r'^`\s*(.*?)`')


def format_exam(exam, update=False):
    name = exam.get('course_name')
    if not update:
        date = datetime.strptime(exam.get('datetime'), "%Y-%m-%d %H:%M:%S")
    else:
        date = datetime.strptime(exam.get('datetime'), "%d/%m/%Y %H:%M:%S")
    date_str = date.strftime("%d/%m/%Y %H:%M")
    today = datetime.today()
    hours = (date - today).total_seconds() / 60 / 60
    days = hours / 24
    hours = (days - int(days)) * 24
    remaining_str = f'{int(days)} days {hours:.2f} hours'
    if days > 0:
        return f'{name.ljust(30)} | {date_str} | {remaining_str}'
    return f'{name.ljust(30)} | {date_str} | Finished! 🏁'


def format_exam_new(exam, update=False):
    name = exam.get('course_name')
    if not update:
        date = datetime.strptime(exam.get('datetime'), "%Y-%m-%d %H:%M:%S")
    else:
        date = datetime.strptime(exam.get('datetime'), "%d/%m/%Y %H:%M:%S")
    date_str = date.strftime("%d/%m/%Y %H:%M")
    today = datetime.today()
    hours = (date - today).total_seconds() / 60 / 60
    days = hours / 24
    hours = (days - int(days)) * 24
    date_str = f'<t:{int(date.timestamp())}>'
    time_str = f'<t:{int(date.timestamp())}:R>'
    if days > 0:
        return f'`{name.ljust(30)}` {time_str} {date_str}'
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

        if (count + 1) % 22 == 0:
            msgs.append(msg + '```')
            msg = '```css\n'

    msgs.append(msg + '```')

    for m in msgs:
        sent_msg = await channel.send(m)
        exam_messages.append(sent_msg.id)

    with open('messages.pickle', 'wb') as f:
        pickle.dump(exam_messages, f)


async def send_message(channel, course, time_left, finished=False):
    channel = client.get_channel(channel)
    if not finished:
        date_str = f'<t:{int(time_left.timestamp())}>'
        time_str = f'<t:{int(time_left.timestamp())}:R>'
        comb = f'{time_str}!\n> Date: {date_str}'
        image = random.choice(exam_memes)
        with open('exam_memes/' + image, 'rb') as f:
            file = discord.File(f)
        return await channel.send(f'**{course}** exam starts {comb}', file=file)
    image = random.choice(finished_memes)
    with open('times_up/' + image, 'rb') as f:
        file = discord.File(f)
    await channel.send(f'**{course}** exam has finished!', file=file)


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
        nickname = 'Exam Countdown!'
        await guild.me.edit(nick=nickname)

    await exams()

    scheduler = AsyncIOScheduler()

    channel = client.get_channel(chosen_channel)
    for msg in exam_messages:
        cron = CronTrigger(minute='0-59', end_date="2022-05-30 16:00:00")
        scheduler.add_job(update_message, cron, args=[channel, msg])

    today = datetime.today()
    for exam in exam_details:
        name = exam.get('course_name')
        date = datetime.strptime(exam.get('datetime'), "%Y-%m-%d %H:%M:%S")
        duration = exam.get('duration').split(':')
        if date < today and len(duration) != 2:
            continue

        # 3 days
        date_3d = date - timedelta(days=3)
        cron = CronTrigger(hour=date_3d.hour, minute=date_3d.minute,
                           day=date_3d.day, month=date_3d.month, year=2022)
        scheduler.add_job(send_message, cron, args=[
                          general_channel, name, date])
        # 1 day
        date_1d = date - timedelta(days=1)
        cron = CronTrigger(hour=date_1d.hour, minute=date_1d.minute,
                           day=date_1d.day, month=date_1d.month, year=2022)
        scheduler.add_job(send_message, cron, args=[
                          general_channel, name, date])
        # 1 hour
        date_1h = date - timedelta(hours=1)
        cron = CronTrigger(hour=date_1h.hour, minute=date_1h.minute,
                           day=date_1h.day, month=date_1h.month, year=2022)
        scheduler.add_job(send_message, cron, args=[
                          general_channel, name, date])
        # finished
        date_f = date + timedelta(hours=int(duration[0]))
        date_f = date_f + timedelta(minutes=int(duration[1]) + 30)
        cron = CronTrigger(hour=date_f.hour, minute=date_f.minute,
                           day=date_f.day, month=date_f.month, year=2022)
        scheduler.add_job(send_message, cron, args=[
                          general_channel, name, date, True])

    scheduler.start()


client.run(TOKEN)
