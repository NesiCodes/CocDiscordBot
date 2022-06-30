import coc
import discord
import asyncio
from decouple import config
import json
import os


def load_coc_client():
    global coc_client
    coc_client = coc.login(
        config('EMAIL'),
        config('PASSWORD'),
        key_names="Made with coc.py by Unejsi",
        client=coc.EventsClient)


def init():
    load_coc_client()


init()

# All variables used for managing clan info and discord bot
global war
global coc_client
linked_accounts = {}
main_channel = config('CHANNEL')
clan_tags = ['#2880UJY0P']
clan_names = ['4G BOYS']
discord_client = discord.Client()


@discord_client.event
async def on_ready():
    print("We have logged in as {0.user}".format(discord_client))
    discord_client.loop.create_task(auto_register())
    discord_client.loop.create_task(check_war_time())
    discord_client.loop.create_task(check_if_war_ended())


@discord_client.event
async def on_message(message):
    if message.content.startswith('/bothelp'):
        await message.channel.send(embed=bot_commands_info())
    if message.content.startswith('#unregister'):
        try:
            message_content = message.content.split()
            special_content = " ".join([n for n in message_content if not (n.isdigit() or n.startswith("#"))])
            unregister(special_content)
        except IndexError as err:
            print(err)
    if message.content.startswith('/usersregistered'):
        await send_registry(message)
    if message.content.startswith('/register'):
        try:
            message_content = message.content.split()
            special_content = " ".join([n for n in message_content if not (n.isdigit() or n.startswith("/"))])
            register(special_content, message.author.id)
        except IndexError as err:
            print(err)
    if message.content.startswith('#registeruser'):
        message_content = message.content.split()
        special_content = " ".join([n for n in message_content if not (n.isdigit() or n.startswith("#"))])
        special_id = " ".join([n for n in message_content if (n.isdigit())])
        register(special_content, special_id)
    if message.author == discord_client.user:
        return
    global war
    if message.content.startswith('!currentwar'):
        await update_war_info(0)
        await get_current_war_and_time(0, message)


async def check_war_time():
    global main_channel
    await discord_client.wait_until_ready()
    main_channel = discord_client.get_channel(int(config('CHANNEL')))
    while not discord_client.is_closed():
        if await time_to_send():
            try:
                await main_channel.send(await get_warning_message())
            except discord.errors.HTTPException as err:
                print(err)
        await asyncio.sleep(3500)  # Checks every hour (3600sec)


async def time_to_send():
    global war
    await update_war_info(0)
    if True:
        try:
            time_remaining = war.end_time.seconds_until / 60  # converts war time to minutes
            hours = time_remaining / 60  # converts wr time to hours
            if hours <= 4 and hours > 0:
                return True
            else:
                return False
        except AttributeError as err:
            print(err)



def register(username, user_id):
    linked_accounts[username] = user_id
    backup_registration()


def unregister(username):
    try:
        linked_accounts.pop(username)
    except Exception:
        print("Unregister: Invalid key (%s)" % username)
    backup_registration()


def backup_registration():
    with open("accounts.json", 'w') as file:
        json.dump(linked_accounts, file)


def load_registration():
    global linked_accounts
    if os.path.exists('accounts.json'):
        linked_accounts = json.load(open('accounts.json', "r"))


async def auto_register():
    message_finish = True
    while(message_finish):
        await asyncio.sleep(5)
        await main_channel.send('Bot started. Auto-Registering users :)')
        await main_channel.send('#registeruser Ghassan 343330938299875329')
        await main_channel.send('#registeruser Worcestershire 746363829780218008')
        await main_channel.send('#registeruser @#boy#@ 883111976606253057')
        await main_channel.send('#registeruser Ashish 883065060308680714')
        await main_channel.send('#registeruser i_3liYz 707937608159854642')
        await main_channel.send('#registeruser iftee 756977831002505327')
        await main_channel.send('#registeruser mulla5h 849307676248899674')
        await main_channel.send('#registeruser Mustafa 434831880937013248')
        await main_channel.send('#registeruser pandey ji 885151624916508683')
        await main_channel.send('#registeruser raid if gay 648488297336799232')
        await main_channel.send('#registeruser RASHID 885274588634828862')
        await main_channel.send('#registeruser Rojiro 449236151698718749')
        await main_channel.send('#registeruser timm 788874533783732264')
        await main_channel.send('#registeruser Tir0nZz1 ✌ 630851105600962565')
        await main_channel.send('#registeruser :skull_crossbones:NARDI:skull_crossbones: 883274288562589727')
        await main_channel.send('#registeruser <<JETULLA>> 329300236424052736')
        await main_channel.send('#registeruser KoKi 329300236424052736')
        await main_channel.send('#registeruser Nesii ✌✔ 329300236424052736')
        message_finish = False
        await asyncio.sleep(5)

async def get_warning_message():
    global war
    if war.is_cwl:
        total_attacks = war.team_size
    else:
        total_attacks = war.team_size * 2
    our_attackers = []  # all members that have attacked
    attacks = 0
    for attack in war.attacks:
        if attack.attacker.clan.name == clan_names[0]:
            our_attackers.append(attack.attacker.name)
            attacks += 1
    await main_channel.send(
        'Our war with ' + war.opponent.name + ' is ending in less than 4 hours...\nWe are currently ' + war.status + ' and have used (' + str(
            attacks) + '/' + str(total_attacks) + ') attacks, the following player have remaining attacks:\n')
    member_list = []  # all members that are in war
    for member in war.clan.members:
        member_list.append(member.name)
    for name in member_list:
        attacks_completed = our_attackers.count(name)
        try:
            user_id = '<@%s>' % str(linked_accounts[name])
        except KeyError:
            user_id = ''
        if war.is_cwl:
            if attacks_completed == 0:
                await main_channel.send(f'{name} you have 1 attack remaining {user_id} ')
        else:
            if attacks_completed == 0:
                await main_channel.send(f'{name} you have 2 attacks remaining {user_id} ')
            elif attacks_completed == 1:
                await main_channel.send(f'{name} you have 1 attack remaining {user_id}')


async def update_war_info(tag):
    global war
    try:
        war = await coc_client.get_current_war(clan_tags[tag])
    except coc.PrivateWarLog:
        print("Clan was private log")
    except coc.errors.Maintenance:
        print("Coc in maintenance")
    except Exception as exception:
        print(type(exception).__name__)
        init()
        war = None
        return


async def send_registry(user_message):
    message = "Currently {0} accounts have been registered!\n".format(len(linked_accounts))
    for name in linked_accounts:
        message += "{0} - <@{1}>\n".format(name, linked_accounts[name])
    message += "To register your account type /register <Account Name>.\n"
    message += "Note that the name MUST be identical to your in game name.\n"
    await user_message.channel.send(message)


async def get_current_war_and_time(tag, message):
    global war
    if war:
        time_remaining = war.end_time.seconds_until / 60  # converts war time to minutes
        hours = int(time_remaining / 60)  # converts wr time to hours
        name = war.opponent.name
        used = 0
        attacks = ''
        for attack in war.attacks:
            if attack.attacker.clan.name == clan_names[tag]:
                used += 1
            if war.is_cwl:
                attacks = str(used) + '/' + str(war.team_size)
            else:
                attacks = str(used) + '/' + str(war.team_size * 2)
        await message.channel.send(
            '{0}\'s current war is against {1}. We have used {2} attacks and are currently {3}, war ends in {4} hours.'.format(
                clan_names[tag],
                name, attacks,
                war.status, hours))
    else:
        await message.channel.send(
            "The war is in a strange CWL state..."
        )


def bot_commands_info():
    message = ''
    message += '**Admin only: #unregister**\n'
    message += 'Unregisters an account format: /unregister ClashName\n\n'
    message += '**/usersregistered**\n'
    message += 'Displays all registered accounts format: /usersregistered\n\n'
    message += '**/register**\n'
    message += 'To register your account type: /register ClashName\n\n'
    message += '**Admin only: #registeruser**\n'
    message += 'Registers a Discord account with a Clash of Clans account format: #registeruser ClashName DiscordID\n\n'
    message += '**!currentwar**\n'
    message += 'Displays information about the current war format: !currentwar\n\n'
    embed = discord.Embed(title="WarHandler Bot Commands:", description=message, color=0xa84300)
    embed.set_thumbnail(url='https://cdn.freelogovectors.net/wp-content/uploads/2019/01/clash_of_clans_logo.png')
    return embed

async def check_if_war_ended():
    global main_channel
    global war
    await update_war_info(0)
    main_channel = discord_client.get_channel(int(config('CHANNEL')))
    if True:
        try:
            time_remaining = war.end_time.seconds_until / 60  # converts war time to minutes
            hours = time_remaining / 60  # converts wr time to hours
            minutes_remaining = int(war.end_time.seconds_until / 60)
            if minutes_remaining == 7 or minutes_remaining == 6 or minutes_remaining == 5 or minutes_remaining == 4 or minutes_remaining == 3 or minutes_remaining == 2 or minutes_remaining == 1 or minutes_remaining == 0:
                try:
                    print(minutes_remaining)
                    await main_channel.send(embed=missed_attacks())
                    await asyncio.sleep(1500)
                except discord.errors.HTTPException as err:
                    print(err)
            await asyncio.sleep(2)
        except AttributeError as err:
            print(err)


def missed_attacks():
    global war
    our_attackers = []
    for attack in war.attacks:
        if attack.attacker.clan.name == clan_names[0]:
            our_attackers.append(attack.attacker.name)
    message = 'Players that missed attacks: \n'
    member_list = []
    for member in war.clan.members:
        member_list.append(member.name)
    for name in member_list:
        attacks_completed = our_attackers.count(name)
        try:
            user_id = '<@%s>' % str(linked_accounts[name])
        except Exception:
            user_id = ''
        if war.is_cwl:
            print('SOON')
        else:
            if attacks_completed == 0:
                message += (name + ' 2 missed ' + user_id + '\n')
            elif attacks_completed == 1:
                message += (name + ' 1 missed ' + user_id + '\n')
    embed = discord.Embed(title='War Against ' + war.opponent.name + 'ended and we ' + war.status + '\n', description=message, color=0x206694)
    # embed.set_thumbnail(url='https://cdn.freelogovectors.net/wp-content/uploads/2019/01/clash_of_clans_logo.png')
    return embed

# This starts the discord client
discord_client.run(config('TOKEN'))
