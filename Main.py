from telethon import TelegramClient, events, Button
from gogoanimeapi import gogoanime as gogo
import formating_results as format
import os

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

try:
    @bot.on(events.NewMessage)
    async def get_latest(event):
        if '/latest' in event.raw_text:
            home_page = gogo.get_home_page()
            (names, ids, epnums) = format.format_home_results(home_page)
            buttonss = []
            for i in range(len(names)):
                try:
                    buttonss.append(
                        [Button.inline(names[i], data=f"lt:{ids[i]}")])
                except:
                    pass
            await bot.send_message(
                event.sender_id,
                'Latest anime added:',
                buttons=buttonss
            )

    @bot.on(events.CallbackQuery)
    async def callback(event):
        data = event.data.decode('utf-8')
        if 'lt:' in data:
            split_data = data.split(":")
            animeid = split_data[-1]
            await send_details(event, animeid)

    @bot.on(events.NewMessage)
    async def start_event(event):
        if '/start' in event.raw_text:
            await bot.send_message(
                event.sender_id,
                'This is a bot that can get links for any anime that is avilable on gogoanime\nUse /anime <Name of anime> to start using this bot\n\n\n*Note: This Bot is still under devlopment if u find any issues, bugs or suggestions contact @President_Shirogane',
                file='https://media.giphy.com/media/b7l5cvG94cqo8/giphy.gif'
            )

    @bot.on(events.NewMessage)
    async def event_handler(event):
        if '/anime' == event.raw_text:
            await bot.send_message(
                event.sender_id,
                'Command must be used like this\n/anime <name of anime>\nexample: /anime One Piece',
                file='https://media1.tenor.com/images/eaac56a1d02536ed416b5a080fdf73ba/tenor.gif?itemid=15075442'
            )

        elif '/anime' in event.raw_text:
            search_result = gogo.get_search_results(event.raw_text[7:])
            try:
                (names, ids) = format.format_search_results(search_result)
                buttons1 = []
                for i in range(len(names)):
                    if len(names[i]) > 55:
                        try:
                            buttons1.append([Button.inline(
                                f"{names[i][:22]}. . .{names[i][-22:]}", data=f"split:{event.raw_text[7:]}:{ids[i][-25:]}")])
                        except:
                            bot.send_message(
                                event.sender_id,
                                "Name u searched for is too long",
                                file='https://media.giphy.com/media/4pk6ba2LUEMi4/giphy.gif'
                            )
                    else:
                        buttons1.append([Button.inline(names[i], data=ids[i])])
                        
                await bot.send_message(
                    event.sender_id,
                    'Search Results:',
                    buttons=buttons1)
            except:
                await bot.send_message(
                    event.sender_id,
                    'Not Found, Check for Typos or search Japanese name',
                    file='https://media.giphy.com/media/4pk6ba2LUEMi4/giphy.gif'
                )

    async def send_details(event, id):
        if 'split:' in id:
            split_id = id.split(":")
            x = gogo.get_search_results(split_id[1])
            (names, ids) = format.format_search_results(x)
            for i in ids:
                if i[-25:] == split_id[2]:
                    id = i
                    break

        search_details = gogo.get_anime_details(id)
        genre = search_details.get('genre')
        x = ''
        for i in genre:
            if i == "'" or i == "[" or i == "]":
                pass
            else:
                x = f'{x}{i}'
        await event.edit('Search Results:')
        try:
            await bot.send_message(
                event.sender_id,
                f"{search_details.get('title')}\nYear: {search_details.get('year')}\nStatus: {search_details.get('status')}\nGenre: {x}\nEpisodes: {search_details.get('episodes')}",
                file=search_details.get('image_url'),
                buttons=[Button.inline(
                    "Download", data=f"Download:{id}:{search_details.get('episodes')}")]
            )
        except:
            await bot.send_message(
                event.sender_id,
                f"{search_details.get('title')}\nYear: {search_details.get('year')}\nStatus: {search_details.get('status')}\nGenre: {x}\nEpisodes: {search_details.get('episodes')}",
                file=search_details.get('image_url'),
                buttons=[Button.inline(
                    "Download", data=f"longdl:{split_id[1]}:{id[-25:]}:{search_details.get('episodes')}")]
            )

    async def send_download_link(event, id, ep_num):
        links = gogo.get_episodes_link(animeid=id, episode_num=ep_num)
        result = format.format_download_results(links)
        await bot.send_message(
            event.sender_id,
            f"Download Links for episode {ep_num}\n{result}"
        )

    @bot.on(events.CallbackQuery)
    async def callback(event):
        data = event.data.decode('utf-8')
        if 'Download' in data:
            x = data.split(":")
            button2 = [[]]
            current_row = 0
            if int(x[2]) < 101:
                for i in range(int(x[2])):
                    button2[current_row].append(Button.inline(
                        str(i+1), data=f'ep:{i+1}:{x[1]}'))
                    if (i+1) % 5 == 0:
                        button2.append([])
                        current_row = current_row + 1
                await event.edit(
                    f'Choose Episode:',
                    buttons=button2
                )
            else:
                num_of_buttons = (int(x[2]) // 100)
                for i in range(num_of_buttons):
                    button2[current_row].append(Button.inline(
                        f'{i}01 - {i+1}00', data=f'btz:{i+1}00:{x[1]}'))
                    if (i+1) % 3 == 0:
                        button2.append([])
                        current_row = current_row + 1
                if int(x[2]) % 100 == 0:
                    pass
                else:
                    button2[current_row].append(Button.inline(
                        f'{num_of_buttons}01 - {x[2]}', data=f'etz:{x[2]}:{x[1]}'))
                await event.edit(
                    f'Choose Episode:',
                    buttons=button2
                )
        elif 'longdl:' in data:
            x = data.split(":")
            button2 = [[]]
            current_row = 0
            search_results = gogo.get_search_results(x[1])
            (names, ids) = format.format_search_results(search_results)
            for i in ids:
                if i[-25:] == x[2]:
                    id = i
                    break
            for i in range(int(x[3])):
                button2[current_row].append(Button.inline(
                    str(i+1), data=f'spp:{i+1}:{x[2]}:{x[1]}'))
                if (i+1) % 5 == 0:
                    button2.append([])
                    current_row = current_row + 1
            await event.edit(
                f'Choose Episode:',
                buttons=button2
            )

    @bot.on(events.CallbackQuery)
    async def callback(event):
        data = event.data.decode('utf-8')
        if 'btz:' in data:
            data_split = data.split(':')
            button3 = [[]]
            current_row = 0
            endnum = data_split[1]
            startnum = int(f'{int(endnum[0])-1}01')
            for i in range(startnum, (int(endnum)+1)):
                button3[current_row].append(Button.inline(
                    str(i), data=f'ep:{i}:{data_split[2]}'))
                if i % 5 == 0:
                    button3.append([])
                    current_row = current_row + 1
            await event.edit(
                f'Choose Episode:',
                buttons=button3
            )
        elif 'etz:' in data:
            data_split = data.split(':')
            button3 = [[]]
            current_row = 0
            endnum = int(data_split[1])
            startnum = int(f'{endnum//100}01')
            for i in range(startnum, (int(endnum)+1)):
                button3[current_row].append(Button.inline(
                    str(i), data=f'ep:{i}:{data_split[2]}'))
                if i % 5 == 0:
                    button3.append([])
                    current_row = current_row + 1
            await event.edit(
                f'Choose Episode:',
                buttons=button3
            )

    @bot.on(events.CallbackQuery)
    async def callback(event):
        data = event.data.decode('utf-8')
        if 'ep:' in data:
            try:
                data_split = data.split(':')
                await send_download_link(event, data_split[2], data_split[1])
            except:
                pass
        elif 'spp:' in data:
            x = data.split(":")
            search_results = gogo.get_search_results(x[3])
            (names, ids) = format.format_search_results(search_results)
            for i in ids:
                if i[-25:] == x[2]:
                    id = i
                    break
            await send_download_link(event, id, x[1])

    @bot.on(events.CallbackQuery)
    async def callback(event):
        id = event.data.decode('utf-8')
        try:
            await send_details(event, id)
        except:
            pass


except Exception as e:
    print(e)


bot.start()

bot.run_until_disconnected()
