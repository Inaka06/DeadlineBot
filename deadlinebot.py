import discord
from discord.ext import commands
import datetime
import pytz
import json
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=')', intents=intents)

scheduler = AsyncIOScheduler()

file_list_tugas = 'listtugas.json'

def load_tasks():
    if os.path.exists(file_list_tugas):
        with open(file_list_tugas, 'r') as file:
            return json.load(file)
    else:
        return []

def save_tasks(task_list):
    with open(file_list_tugas, 'w') as file:
        json.dump(task_list, file, indent=2)

list_tugas = load_tasks()

time_zone = 'Asia/Jakarta'
sekarang = datetime.datetime.now(pytz.timezone(time_zone))
hari = sekarang.weekday() + 1

jadwalhariini = {}

if hari == 1:
    jadwalhariini = {
        1: 'Informatika',
        2: 'Bahasa Jepang',
        3: 'Bahasa Indonesia',
        4: 'PAIBP'
    }
elif hari == 2:
    jadwalhariini = {
        1: 'Matematika Umum',
        2: 'Bahasa Jepang',
        3: 'Informatika',
        4: 'Seni Budaya',
        5: 'Sejarah'
    }
elif hari == 3:
    jadwalhariini = {
        1: 'Olahraga',
        2: 'Bahasa Inggris Lanjut',
        3: 'Matematika Terapan',
        4: 'Sejarah',
        5: 'Bahasa Jawa',
        6: 'PPKn'
    }
elif hari == 4:
    jadwalhariini = {
        1: 'Matematika Terapan',
        2: 'PKWU',
        3: 'Bahasa Inggris Lanjut',
        4: 'PPKn',
        5: 'Matematika Umum',
    }
elif hari == 5:
    jadwalhariini = {
        1: 'Bahasa Inggris',
        2: 'Bahasa Indonesia',
        3: 'Projek',
        4: 'Pramuka',
        5: 'Bahasa Jerman'
    }

@bot.event
async def on_ready():
    print("Bot sudah Online!")
    print(hari)
    scheduler.start()

    async def decrease_deadlines():
        global list_tugas
        print("Decreasing deadlines...")
        for task in list_tugas:
            task['deadline'] -= 1
        save_tasks(list_tugas)
        list_tugas = load_tasks() 

    scheduler.add_job(decrease_deadlines, 'cron', hour=12, minute=0, second=0, timezone=time_zone)

    async def notify_deadline():
        tomorrow = datetime.datetime.now(pytz.timezone(time_zone)) + datetime.timedelta(days=1)
        if tomorrow.weekday() < 5: 
            tasks_tomorrow = [task for task in list_tugas if task['deadline'] == 1]
            if tasks_tomorrow:
                role_mention = '<<@&1175049934756663316>>' 
                await bot.get_channel(1087355733546385500).send(f"{role_mention} Kamu punya {len(tasks_tomorrow)} tugas untuk besok!")

    scheduler.add_job(notify_deadline, 'cron', hour=15, minute=0, second=0, timezone=time_zone)
    scheduler.add_job(notify_deadline, 'cron', hour=20, minute=0, second=0, timezone=time_zone)


@bot.command(name='hello', help='Say hello to bot!')
async def hello(ctx):
    await ctx.send('Hello, {}!'.format(ctx.author.mention))


@bot.command(name='jadwal', help='menampilkan jadwal hari ini')
async def jadwal(ctx):
    await ctx.send(f'```python\n{jadwalhariini}```')


@bot.command(name='tugas', help=')tugas (nomor_mapel) (jauh_deadline)')
async def tugas(ctx, nomor_mapel: int, jauh_deadline: int):
    if nomor_mapel <= len(jadwalhariini) and jauh_deadline >= 1:
        mapeltugas = jadwalhariini.get(nomor_mapel, {})
        await ctx.send(f'Tugas {mapeltugas} telah tercatat dengan deadline {jauh_deadline} hari.')
        detail_tugas = {'mapel': mapeltugas, 'deadline': jauh_deadline}

    list_tugas.append(detail_tugas)
    with open(file_list_tugas, 'w') as file:
        json.dump(list_tugas, file, indent=2)
        
@bot.command(name='lihattugas', help='Melihat daftar tugas yang harus diselesaikan')
async def lihattugas(ctx):
    sorted_list_tugas = sorted(list_tugas, key=lambda x: x['deadline'])

    if sorted_list_tugas:
        task_str = '\n'.join(f'{i+1}. {task["mapel"]}, deadline {task["deadline"]} hari' for i, task in enumerate(sorted_list_tugas))
        await ctx.send(f'Daftar Tugas:\n```{task_str}```')
    else:
        await ctx.send('Tidak ada tugas yang harus diselesaikan.')


@bot.command(name='hapustugas', help='Menghapus semua tugas dari file')
async def hapustugas(ctx):
    global list_tugas
    list_tugas = []
    save_tasks(list_tugas)
    list_tugas = load_tasks()
    await ctx.send('Semua tugas telah dihapus dari file.')

bot.run('token')
