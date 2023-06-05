import json
import discord
from discord.ext import commands
import asyncio
import aiohttp
import csv
from datetime import datetime, date, time, timezone
import matplotlib.pyplot as plt
import pandas as pd
import io

tok='' #test

bot = commands.Bot(command_prefix = '.', help_command=None)

pol = ''

@bot.event
async def on_ready():
    print(bot.user.name)
    bot.session = aiohttp.ClientSession()


async def get_data(session, symb: str):
    try:
        await bot.wait_until_ready()
        channel = bot.get_channel(1113228880162078841)
        dat = datetime.now(timezone.utc).strftime('%Y-%m-%d')

        url = f'https://api.polygon.io/v2/aggs/ticker/{symb}/range/1/week/2021-07-22/{dat}?adjusted=true&sort=desc&limit=1000&apiKey={pol}'
        async with session.get(url, verify_ssl=False) as resp1:
            temp1 = json.loads(await resp1.text())
            df = pd.DataFrame(temp1["results"])

            tocka = df.loc[0]['c']
            t = df

            perviy_nijniy = df.loc[2:8]['c'].min()
            perviy_nijniy_index = df.loc[2:8]['c'].idxmin()

            perviy_verhniy = df.loc[(perviy_nijniy_index+1):(8+perviy_nijniy_index)]['c'].max()
            perviy_verhniy_index = df.loc[(perviy_nijniy_index+1):(8+perviy_nijniy_index)]['c'].idxmax()

            vtoroy_nijniy = df.loc[(perviy_verhniy_index+1):(8+perviy_verhniy_index)]['c'].min()
            vtoroy_nijniy_index = df.loc[(perviy_verhniy_index+1):(8+perviy_verhniy_index)]['c'].idxmin()

            vtoroy_verhniy = df.loc[(vtoroy_nijniy_index+1):(8+vtoroy_nijniy_index)]['c'].max()
            vtoroy_verhniy_index = df.loc[(vtoroy_nijniy_index+1):(8+vtoroy_nijniy_index)]['c'].idxmax()

            prom = df.loc[(perviy_verhniy_index+1):vtoroy_nijniy_index]['c'].max()

            
            ###################
            open_perviy_verhniy = df.loc[(perviy_nijniy_index+1):(8+perviy_nijniy_index)]['o'].max()
            open_vtoroy_nijniy = df.loc[(perviy_verhniy_index+1):(8+perviy_verhniy_index)]['o'].max()

            if perviy_nijniy >= vtoroy_nijniy:
                percent = ((perviy_nijniy - vtoroy_nijniy)/vtoroy_nijniy)*100
            elif perviy_nijniy < vtoroy_nijniy:
                percent = ((vtoroy_nijniy - perviy_nijniy)/perviy_nijniy)*100

            if perviy_verhniy > vtoroy_verhniy:
                percent_2 = ((perviy_verhniy-vtoroy_verhniy)/vtoroy_verhniy)*100
            elif perviy_verhniy < vtoroy_verhniy:
                percent_2 = ((vtoroy_verhniy - perviy_verhniy)/perviy_verhniy)*100

            percent_3 = ((perviy_verhniy-perviy_nijniy)/perviy_nijniy)*100
            percent_4 = ((vtoroy_verhniy-vtoroy_nijniy)/vtoroy_nijniy)*100

            if perviy_verhniy > tocka and percent <= 7 and percent_2 <= 7 and prom < perviy_verhniy and vtoroy_nijniy < vtoroy_verhniy and perviy_verhniy > open_perviy_verhniy and perviy_verhniy > open_vtoroy_nijniy and perviy_nijniy < tocka:
                if (perviy_verhniy_index-perviy_nijniy_index)>2 and (vtoroy_nijniy_index-perviy_verhniy_index)>2 and (vtoroy_verhniy_index-vtoroy_nijniy_index)>2 and percent_3 >= 10 and percent_4 >= 10:
                    a = df.loc[:vtoroy_verhniy_index]
                    df = a[::-1].reset_index(drop=True)

                    plt.figure()

                    up = df[df.c >= df.o]

                    down = df[df.c < df.o]

                    col1 = 'green'

                    col2 = 'red'

                    width = .7
                    width2 = .03

                    plt.bar(up.index, up.c-up.o, width, bottom=up.o, color=col1)
                    plt.bar(up.index, up.h-up.c, width2, bottom=up.c, color=col1)
                    plt.bar(up.index, up.l-up.o, width2, bottom=up.o, color=col1)

                    plt.bar(down.index, down.c-down.o, width, bottom=down.o, color=col2)
                    plt.bar(down.index, down.h-down.o, width2, bottom=down.o, color=col2)
                    plt.bar(down.index, down.l-down.c, width2, bottom=down.c, color=col2)

                    plt.xticks(rotation=30, ha='right')
                    ax=plt.axes()
                    ax.set_facecolor('black')

                    plt.title(f"{symb}\nTF: {'WEEK'}", fontsize=15, color="white")
                    png_wrapper = io.BytesIO()
                    bg_color = "#000000"
                    plt.savefig(png_wrapper, format='png', facecolor=bg_color)
                    png_wrapper.seek(0)
                    filename = (symb) + ".png"
                    await channel.send(file=discord.File(png_wrapper, filename=filename))

                    png_wrapper.close()
                    plt.close()

    except Exception:
         pass
           
            

async def site_data():
    # while True:
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                with open('stock.csv', newline='') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            stock = row['Symbol']
                            task = asyncio.create_task(get_data(session, stock))
                            tasks.append(task)
                        await asyncio.gather(*tasks)
        except Exception:
            pass

bot.loop.create_task(site_data())
bot.run(tok)
