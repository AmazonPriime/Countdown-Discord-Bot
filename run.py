from datetime import datetime
import os
import asyncio
import json

import discord
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

gifs = [x for x in os.listdir() if x.endswith(
    '.gif') and x != "lotr-frodo.gif"]

with open("exams.json") as f:
    exam_details = json.load(f)

sad_project_id = 837389562878623764
my_channel_id = 873129698069188638

diss_date = datetime.strptime('2022-04-01 17:00:00', "%Y-%m-%d %H:%M:%S")


async def update_nickname():
    await client.wait_until_ready()
    while True:
        # get todays date and calc mins left
        today = datetime.today()
        minutes = int((diss_date - today).total_seconds() / 60)
        nickname = ""
        # end of countdown update nickname
        if minutes <= 0:
            for guild in client.guilds:
                nickname = 'Hi :)'
                await guild.me.edit(nick=nickname)
            print(f'{today}: It is over. End of countdown to {diss_date}')
            break
        for guild in client.guilds:
            try:
                if '69' in str(minutes) or '420' in str(minutes):
                    nickname = f'👌 {minutes} mins left'
                    await guild.me.edit(nick=nickname)
                else:
                    nickname = f'{minutes} mins left'
                    await guild.me.edit(nick=nickname)
            except Exception as e:
                print(guild)
                print(e)
        print(f'{today}: Updated nickname to: {nickname}')
        await asyncio.sleep(60)  # task runs every 1 minute


async def sendMessage(filename=False):
    channel = client.get_channel(sad_project_id)
    today = datetime.today()
    hours = (diss_date - today).total_seconds() / 60 / 60
    horn = "🎺"
    msg = f'{horn*2} **ANNOUNCEMENT *{hours:.2f}*  hours left!!** {horn*2}'
    if hours >= 0:
        if not filename:
            if len(gifs) > 0:
                await channel.send(msg, file=discord.File(gifs.pop()))
            else:
                await channel.send(msg)
        else:
            await channel.send(msg, file=discord.File(filename))


async def sendMessageCheck(filename=False):
    channel = client.get_channel(sad_project_id)
    horn = "🎺"
    msg = f'{horn*4} Remember to submit!! Deadline for those without an' + \
        ' extension is in **30 minutes!!** We\'re almost there!'
    await channel.send(msg, file=discord.File('psa.png'))


async def sendMessageEnd(filename=False):
    channel = client.get_channel(sad_project_id)
    horn = "🎺"
    party = "🎉"
    msg = f'{horn}{party*2}{horn} **ITS OVER!!!!** {horn}{party*2}{horn}'
    await channel.send(msg, file=discord.File('lotr-frodo.gif'))
    sparkle = "✨"
    gold = "🥇"
    msg = f'{sparkle*2} Have a peak at my discord profile for a little {gold}' + \
        f' reward, you all deserve it!'
    await channel.send(msg)


def print_exam(exam):
    name = exam.get('course_name')
    code = exam.get('course_code')
    date = exam.get('datetime')
    return f'{name} [{code}] - {date}'


@client.command()
async def exam(ctx, code):
    if not code:
        return await ctx.send("Please specify a course code or use $exams. :)")

    for exam in exam_details:
        is_code = exam.get('course_code').lower() == code.lower()
        has_number = exam.get('course_code')[7:] == code
        if is_code or has_number:
            await ctx.send(print_exam(exam))


@client.command()
async def exams(ctx):
    msgs = []
    msg = ''
    for exam in exam_details:
        name = exam.get('course_name')
        code = exam.get('course_code')
        date = datetime.strptime(exam.get('datetime'), "%Y-%m-%d %H:%M:%S")
        date_str = date.strftime("%d/%m/%Y @ %H:%M")
        today = datetime.today()
        hours = int((date - today).total_seconds() / 60 / 60)
        msg += f'{name} [*{code}*]: {date_str} starts in {hours} hours\n'
        if len(msg) > 1000:
            msgs.append(msg)
            msg = ''
    for m in msgs:
        await ctx.send(m)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    scheduler = AsyncIOScheduler()

    cron = CronTrigger(start_date="2022-04-01",
                       hour="6-16/2",
                       minute=0,
                       end_date="2022-04-01 16:00:00")
    scheduler.add_job(sendMessage, cron)

    cron = CronTrigger(start_date="2022-04-01",
                       hour="16",
                       minute="0,15,30,45",
                       end_date="2022-04-01 17:00:00")
    scheduler.add_job(sendMessage, cron)

    cron = CronTrigger(start_date="2022-04-01",
                       hour=16,
                       minute=30,
                       end_date="2022-04-01 18:00:00")
    scheduler.add_job(sendMessageCheck, cron)

    cron = CronTrigger(start_date="2022-04-01",
                       hour=17,
                       minute=0,
                       end_date="2022-04-01 18:00:00")
    scheduler.add_job(sendMessageEnd, cron)

    scheduler.start()


client.loop.create_task(update_nickname())
client.run(TOKEN)
