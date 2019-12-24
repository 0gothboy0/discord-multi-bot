import discord
from discord.ext import commands
import discord.voice_client
import asyncio
import pytz, datetime
from giphypop import translate
import mysql.connector
from colorama import init
init()
from colorama import Fore
import logging
import time

start_time = time.time()
time_now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))







maindb = mysql.connector.connect(user='LOGIN', password='PASS',
                               host='localhost', database='DB',
                               auth_plugin='mysql_native_password')

mycursor = maindb.cursor()


giphy_api_key = "GIPHY_TOKEN"
bot = commands.Bot(command_prefix='!')



logging.basicConfig(filename=f'app_{time_now}.log', filemode='w',format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def db_select(user_id):
    sql = f"SELECT * FROM main WHERE id = {user_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    result_step_one = " ".join(str(x) for x in myresult)
    result_step_two = result_step_one.replace(")", "")
    result_step_three = result_step_two.replace("(", "")
    result = result_step_three.replace("'", "")
    return result


def db_insert(user_id, param_one,param_two,param_three, param_four):
    sql = "INSERT INTO main (id, cookies, flower_one, flower_two, bonus) VALUES (%s, %s, %s, %s, %s)"
    val = (user_id, param_one, param_two, param_three, param_four)
    mycursor.execute(sql, val)
    maindb.commit()

def db_update(colum_id, user_id, user_param):
    sql = f"UPDATE main SET {colum_id} = {user_param} WHERE id = {user_id}"
    mycursor.execute(sql)
    maindb.commit()

def db_update_special_minus(colum_id, user_id, user_param, user_value):
    sql = f"UPDATE main SET {colum_id} = {user_param} - {user_value} WHERE id = {user_id}"
    mycursor.execute(sql)
    maindb.commit()

def db_update_special_plus(colum_id, user_id, user_param, user_value):
    sql = f"UPDATE main SET {colum_id} = {user_param} + {user_value} WHERE id = {user_id}"
    mycursor.execute(sql)
    maindb.commit()

while True:
# --------------------- БОТ



    @bot.event
    async def on_ready():
        print('------------------------')
        print('wOw thats works')
        print(bot.user.name)
        print(bot.user.id)
        print('------------------------')




    @bot.command(pass_context=True)
    async def ping(ctx):
        """ Pong! """
        before = time.monotonic()
        message = await ctx.send("🌻Pong!")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🌻Pong!  `{int(ping)}ms`")
        print(Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: PING {int(ping)}ms")



    @bot.command()
    async def bot_help(ctx):
        embed=discord.Embed(title=" ", color=0xff40ff)
        embed.set_author(name="Список всех команд:", url="https://vk.com/id320547639")
        embed.add_field(name="!mute", value="мут пользователя навсегда, указывается в формате !mute<имя пользователя>.", inline=False)
        embed.add_field(name="!unmute", value="снятие мута, указывается в формате !unmute<имя пользователя>.", inline=False)
        embed.add_field(name="!tmute", value="временный мут, указывается в формате !tmute<время><имя пользователя>.", inline=True)
        embed.add_field(name="!akick", value="кик пользователя с анимацией, указывается в формате !akick<имя пользователя>.", inline=True)
        embed.add_field(name="!kick", value="кик пользователя, указывается в формате !kick<имя пользователя>.", inline=True)
        embed.add_field(name="!ban", value="бан пользователя, указывается в формате !ban<имя пользователя>.", inline=True)
        embed.set_footer(text="как же я устал делать все это..")
        await ctx.send(embed=embed)
        logging.info(Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} USE COMMAND !BOT_HELP ")





    # ---------------------------------- АДМИНСКАЯ ЧАСТЬ


    # ВРЕМЕННЫЙ МУТ
    @bot.command()
    @commands.has_role('МэЙби бЭйбИ')
    async def tmute(ctx, time: int, member: discord.Member = None):
        if not member and not time:
            await ctx.send("```🥀 Выберите пользователя и введите время мута.```")
            return
        elif not member:
            await ctx.send("```🥀 Выберите пользователя.```")
            return
        elif not time:
            await ctx.send("```🌻 Введите время мута, или используйте команду \"!mute @user\".```")
            return
        elif member and time:
            role = discord.utils.get(ctx.guild.roles, name="замучен")
            embed1=discord.Embed(title=f"{member.display_name}",description=f"{member.mention} был замучен.\n\nАдминистратор - {ctx.message.author.mention}.", color=0xff00f6)
            embed1.set_footer(text=f"{time_now}")
            img_muted = translate('muted', api_key=giphy_api_key)
            embed1.set_image(url=img_muted.media_url)
            await ctx.send(embed=embed1)
            await member.add_roles(role)
            await asyncio.create_task(unmute_task(ctx, member, role, time))
            await ctx.send(f"{member.mention} был размучен.\n\nСрок блокировки - {time}.\n\nАдминистратор - {ctx.message.author.mention}.", color=0xff00f6)
            logging.warning(Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} TMUTE USER {member.display_name} ON {time} SECONDS!")

    @tmute.error
    async def tmute_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🌻 У вас недостаточно прав, чтобы использовать данную команду.```")
            logging.warning(Fore.LIGHTRED_EX + f"{time_now} | NEW EVENT ERROR: USER {ctx.message.author.display_name} TRIED USE COMMAND TMUTE!")

    async def unmute_task(ctx, member, role, time):
        await asyncio.sleep(time)
        await member.remove_roles(role)


    # ВЕЧНЫЙ МУТ


    @bot.command()
    @commands.has_role('МэЙби бЭйбИ')
    async def mute(ctx, member: discord.Member = None):
        if not member:
            await ctx.send("```🥀 Выберите пользователя.```")
            return
        elif member:
            role = discord.utils.get(ctx.guild.roles, name="замучен")
            embed1=discord.Embed(title=f"{member.display_name}",description=f"{member.mention} был замучен.\n\nАдминистратор - {ctx.message.author.mention}.", color=0xff00f6)
            embed1.set_footer(text=f"{time_now}")
            img_muted = translate('muted', api_key=giphy_api_key)
            embed1.set_image(url=img_muted.media_url)
            await ctx.send(embed=embed1)
            await member.add_roles(role)
            logging.warning(Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} MUTE USER {member.display_name}!")

    @mute.error
    async def mute_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🥀 У вас недостаточно прав, чтобы использовать данную команду.```")
            logging.warning(Fore.LIGHTRED_EX + f"{time_now} | NEW EVENT ERROR: USER {ctx.message.author.display_name} TRIED USE COMMAND MUTE!")

    # РАЗМУТ ВЕЧНОГО БАНА


    @bot.command()
    @commands.has_role('МэЙби бЭйбИ')
    async def unmute(ctx, member: discord.Member = None):
        if not member:
            await ctx.send("```🥀 Выберите пользователя.```")
            return
        elif member:
            role = discord.utils.get(ctx.guild.roles, name="замучен")
            embed1=discord.Embed(title=f"{member.display_name}", description=f"{member.mention} был размучен.\n\nАдминистратор - {ctx.message.author.mention}.", color=0xff00f6)
            embed1.set_footer(text=f"{time_now}")
            img_unmute = translate('unmuted', api_key=giphy_api_key)
            embed1.set_image(url=img_unmute.media_url)
            await ctx.send(embed=embed1)
            await member.remove_roles(role)
            logging.warning(Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} UNMUTE USER {member.display_name}!")

    @mute.error
    async def unmute_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🥀 У вас недостаточно прав, чтобы использовать данную команду.```")
            logging.warning(Fore.LIGHTRED_EX + f"{time_now} | NEW EVENT ERROR: USER {ctx.message.author.display_name} TRIED USE COMMAND UNMUTE")





    # КИК С АНИМАЦИЕЙ


    @bot.command()
    @commands.has_permissions(administrator=True)
    async def akick(ctx, member:discord.Member = None):
        if not member:
            await ctx.send("```🥀 Выберите пользователя.```")
            return
        gavno = await ctx.send(
    f'\n┓┏┓┏┓┃＼○／  @{member.mention}: не понял'
    '\n┛┗┛┗┛┃ / /'
    '\n┓┏┓┏┓┃ノ'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃ ! уле=еле !')
        time.sleep(0.5)
        await gavno.edit(content=

    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    f'\n┓┏┓┏┓┃＼○／  @{member.mention}: нинада пРоШу!!!!!!'
    '\n┛┗┛┗┛┃ / /'
    '\n┓┏┓┏┓┃ノ'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃ ! уле=еле !')
        time.sleep(0.5)
        await gavno.edit(content=
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    f'\n┓┏┓┏┓┃＼○／  @{member.mention}: СТОЙ, ОСТАНОВИСЬ'
    '\n┛┗┛┗┛┃ / /'
    '\n┓┏┓┏┓┃ノ'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃ ! уле=еле !')
        time.sleep(0.5)
        await gavno.edit(content=
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    '\n┓┏┓┏┓┃'
    '\n┛┗┛┗┛┃'
    f'\n┓┏┓┏┓┃＼○／  @{member.mention}: ПРИВЕТ МАМЕ ЧМО ЕБАНОЕ!!!!!!'
    '\n┛┗┛┗┛┃ / /'
    '\n┓┏┓┏┓┃ノ'
    '\n┛┗┛┗┛┃ ! уле=еле !')
        time.sleep(0.5)
        await member.kick()
        await gavno.edit(content=f"```{member.mention} был кикнут к хУяМ!```")
        logging.warning(
            Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} AKICK USER {member.display_name}!")


    @akick.error
    async def akick_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🥀 У вас недостаточно прав, чтобы использовать данную команду.```")
            logging.warning(Fore.LIGHTRED_EX + f"{time_now} | NEW EVENT ERROR: USER {ctx.message.author.display_name} TRIED USE COMMAND AKICK!")





    # ОБЫЧНЫЙ КИК


    @bot.command()
    @commands.has_permissions(administrator=True)
    async def kick(ctx, member:discord.Member = None):
        if not member:
            await ctx.send("```🥀 Выберите пользователя.```")
            return
        elif member:
            embed1=discord.Embed(title=f"{member.display_name}", description=f"{member.mention} был кикнут.\n\nАдминистратор - {ctx.message.author.mention}.", color=0xff00f6)
            embed1.set_footer(text=f"{time_now}")
            img_kick = translate('kicked', api_key=giphy_api_key)
            embed1.set_image(url=img_kick.media_url)
            await ctx.send(embed=embed1)
            await member.kick()
            logging.warning(Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} KICK USER {member.display_name}!")

    @kick.error
    async def kick_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🥀 У вас недостаточно прав, чтобы использовать данную команду.```")
            logging.warning(Fore.LIGHTRED_EX + f"{time_now} | NEW EVENT ERROR: USER TRIEN USE COMMAND KICK!")


    # БАН ПОЛЬЗОВАТЕЛЯ




    @bot.command()
    @commands.has_permissions(administrator=True)
    async def ban(ctx, member:discord.Member = None):
        if not member:
            await ctx.send("```🥀 Выберите пользователя.```")
            return
        elif member:
            embed1=discord.Embed(title=f"{member.display_name}", description=f"{member.mention} был забанен.\n\nАдминистратор - {ctx.message.author.mention}.", color=0xff00f6)
            embed1.set_footer(text=f"{time_now}")
            img_banned = translate('banned', api_key=giphy_api_key)
            embed1.set_image(url=img_banned.media_url)
            await ctx.send(embed=embed1)
            await member.ban()
            logging.warning(
                Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} BAN USER {member.display_name}!")

    @ban.error
    async def ban_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🌻 У вас недостаточно прав, чтобы использовать данную команду.```")
            logging.warning(Fore.LIGHTRED_EX + f"{time_now} | NEW EVENT ERROR: USER TRIEN USE COMMAND BAN!")

    @bot.command()
    @commands.has_role('МэЙби бЭйбИ')
    async def reg(ctx, member: discord.Member = None):
        if not member:
            db_insert(f"{ctx.author.id}","5","1","1","0")
            await ctx.send("```🌻 Успешно!```")
            logging.warning(
                Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} REG HIMSELF!")
        if member:
            db_insert(f"{member.id}", "5", "1", "1","0")
            await ctx.send("```🌻 Успешно!```")
            logging.warning(
                Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} REG USER {member.display_name}!")



    @bot.command()
    @commands.has_permissions(administrator=True)
    async def check(ctx, member: discord.Member = None):
        if not member:
            test = db_select(ctx.author.id)
            await ctx.send(f"```{test}```")
            logging.warning(
                Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} CHECK HIMSELF!")
        elif member:
            test = db_select(member.id)
            await ctx.send(f"```{test}```")
            logging.warning(
                Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} CHECK USER {member.display_name}!")




    @bot.command()
    @commands.has_permissions(administrator=True)
    async def upd(ctx, user_param: str,user_value: int, member: discord.Member = None):
        if user_param != "id":
            if not member:
                db_update(user_param, ctx.author.id, user_value)
                await ctx.send(f"```🌻 Успешно!```")
                logging.critical(
                    Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} UPDATE {user_param}|{user_value}!")
            elif member:
                db_update(user_param, member.id, user_value)
                await ctx.send(f"```🌻 Успешно!```")
                logging.critical(
                    Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} UPDATE {user_param}|{user_value}| IN USER {member.display_name}!")
        if user_param == "id":
            await ctx.send("```🥀 Параметр \'id\' запрещено обновлять.```")


    @bot.command()
    @commands.has_permissions(administrator=True)
    async def add(ctx, user_param: str,user_value: int, member: discord.Member = None):
        if user_param != "id":
            if not member:
                db_update_special_plus(user_param, ctx.author.id, user_param, user_value)
                logging.critical(
                    Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} UPDATE {user_param}|{user_value}!")
            elif member:
                db_update_special_plus(user_param, member.id, user_param, user_value)
                logging.critical(
                    Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: ADMIN {ctx.message.author.display_name} UPDATE {user_param}|{user_value}| IN USER {member.display_name}!")
        if user_param == "id":
            await ctx.send("```🥀 Параметр \'id\' запрещено обновлять.```")






    # ---------------------------------- ПОЛЬЗОВАТЕЛЬСКАЯ ЧАСТЬ


    @bot.command()
    async def hug(ctx, member:discord.Member = None):
        if not member:
            await ctx.send("```🥀 Данного пользователя не существует!```")
        elif member:
            embed1 = discord.Embed(title="owo 💕🔫", description=f"{ctx.message.author.mention} обнял {member.mention} ❤️",color=0xff00f6)
            img_hug = translate('anime hug', api_key=giphy_api_key)
            embed1.set_image(url=img_hug.media_url)
            await ctx.send(embed=embed1)

    @hug.error
    async def hug_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🥀 К сожалению что-то пошло не так.```")



    @bot.command()
    async def pat(ctx, member: discord.Member = None):
        if not member:
            await ctx.send("```🥀 Данного пользователя не существует!```")
        elif member:
            embed1 = discord.Embed(title="owo 💕🔫", description=f"{ctx.message.author.mention} погладил {member.mention} ❤️",
                                   color=0xff00f6)
            embed1.set_image(url='https://media.giphy.com/media/5tmRHwTlHAA9WkVxTU/giphy.gif')
            await ctx.send(embed=embed1)

    @pat.error
    async def pat_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("``` 🌻 К сожалению что-то пошло не так.```")


    @bot.command()
    async def suicide(ctx):
        embed1 = discord.Embed(title=f"Прощай {ctx.message.author}",
                               description=f"{ctx.message.author.mention} выбрал легкий путь...😢️",
                               color=0xff00f6)
        img_cry = translate('anime cry', api_key=giphy_api_key, )
        embed1.set_image(url=img_cry.media_url)
        await ctx.send(embed=embed1)
        member = ctx.message.author
        await member.kick()
        logging.critical(
            Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} USE COMMAND SUICIDE!")

    @suicide.error
    async def suicide_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("``` 🥀 К сожалению что-то пошло не так.```")

    @bot.command()
    async def cookie(ctx, member: discord.Member = None):
        if member.id == ctx.author.id:
            await ctx.send("```🥀 Вы не можете дать печенье самому себе.```")
        elif member.id != ctx.author.id:
            db_update_special_minus("cookies", ctx.author.id, "cookies", 1)

            db_update_special_plus("cookies", member.id, "cookies", 1)
            user_cookies_step_one = db_select(member.id)
            user_cookies_step_two = user_cookies_step_one.split()[1]
            user_cookies = user_cookies_step_two.replace(",", "")

            embed1 = discord.Embed(title="",
                                   description=f"{ctx.message.author.mention} дал одну печеньку {member.mention}️\n\nСейчас их {user_cookies} 🍪", color=0xff00f6)
            embed1.set_image(url='https://media.giphy.com/media/Vc02uJFtpTiQRylOQg/giphy.gif')

            await ctx.send(embed=embed1)
            logging.warning(
                Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} GIVE ONE COOKIE {member.display_name}!")


    @bot.command()
    async def bag(ctx):
        bag_step_one = db_select(ctx.author.id)
        bag_step_two = bag_step_one.split()[1]
        user_bag_cookies = bag_step_two.replace(",", "")

        bag_step_flower_one = bag_step_one.split()[2]
        user_bag_flower_one = bag_step_flower_one.replace(",", "")

        bag_step_flower_two = bag_step_one.split()[3]
        user_bag_flower_two = bag_step_flower_two.replace(",", "")

        embed1 = discord.Embed(title="🎒 Рюкзак",
                               description=f"Сейчас в вашем рюкзаке лежит:\n```{user_bag_cookies} 🍪 | {user_bag_flower_one} 🌻 | {user_bag_flower_two} 🌺```",
                               color=0xff00f6)
        embed1.set_image(url='https://media.giphy.com/media/h4C5cCuVDxOtPdzLAC/giphy.gif')

        await ctx.send(embed=embed1)

    @bag.error
    async def bag_error(ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("```🥀 У вас нет своего рюкзака. Чтобы получить введите !get_bag.```")



    @bot.command()
    async def get_bag(ctx):
        db_insert(f"{ctx.author.id}","10","1","1", "0")
        await ctx.send("```🌻 Поздравляю! Вы успешно получили рюкзак! Введите !bag чтобы посмотреть его содержимое.```")

    @get_bag.error
    async def get_bag_error(ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("```🥀 У вас уже есть свой рюкзак. Введите !bag чтобы посмотреть его содержимое.```")





    role_one_cost = 999
    role_two_cost = 1999
    role_three_cost = 3999
    role_four_cost = 7999
    role_five_cost = 9999






    @bot.command()
    async def shop(ctx):
        embed1 = discord.Embed(title="🛒 Магазин",
                               description=f"Товары, которые можно купить за печенье 🍪:"
                                           f"\n```1. clown 🤡 - {role_one_cost} 🍪"
                                           f"\n2. bad guy - {role_two_cost} 🍪"
                                           f"\n3. дело - {role_three_cost} 🍪"
                                           f"\n4. ваша персональная роль - {role_four_cost} 🍪"
                                           f"\n5. мут пользователя - {role_five_cost} 🍪```"
                                           f"\nЧтобы купить, введите !buy <номер товара в магазине>.",
                               color=0xff00f6)
        embed1.set_image(url='https://media.giphy.com/media/MdwKfOxv6CgRqwmbnx/giphy.gif')

        await ctx.send(embed=embed1)



    @bot.command()
    async def buy(ctx, value: int):
        member = ctx.author

        step_one = db_select(ctx.author.id)
        step_two = step_one.split()[1]
        user_cookies = step_two.replace(",", "")
        if value == 1:
            role = discord.utils.get(ctx.guild.roles, name="clown 🤡")
            user_test = int(user_cookies) - role_one_cost
            if user_test > 0:
                if role not in ctx.author.roles:
                    db_update_special_minus("cookies", ctx.author.id, "cookies", role_one_cost)
                    await member.add_roles(role)
                    await ctx.send("```Поздравляю, вы успешно купили роль clown 🤡```")
                    logging.critical(
                        Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} BOUGHT ROLE 1!")
                elif role in ctx.author.roles:
                    await ctx.send("```🥀 У вас уже есть эта роль.```")
            else:
                await ctx.send("```🥀 Вам не хватает печенья!```")

        elif value == 2:
            role = discord.utils.get(ctx.guild.roles, name="дело")
            user_test = int(user_cookies) - role_two_cost
            if user_test > 0:
                if role not in ctx.author.roles:
                    db_update_special_minus("cookies", ctx.author.id, "cookies", role_two_cost)
                    await member.add_roles(role)
                    await ctx.send("```Поздравляю, вы успешно купили роль дело```")
                    logging.critical(
                        Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} BOUGHT ROLE 2!")
                elif role in ctx.author.roles:
                    await ctx.send("```🥀 У вас уже есть эта роль.```")
            else:
                await ctx.send("```🥀 Вам не хватает печенья!```")
        elif value == 3:
            role = discord.utils.get(ctx.guild.roles, name="bad guy")
            user_test = int(user_cookies) - role_three_cost
            if user_test > 0:
                if role not in ctx.author.roles:
                    db_update_special_minus("cookies", ctx.author.id, "cookies", role_three_cost)
                    await member.add_roles(role)
                    await ctx.send("```Поздравляю, вы успешно купили роль bad guy```")
                    logging.critical(Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} BOUGHT ROLE 3!")
                elif role in ctx.author.roles:
                    await ctx.send("```🥀 У вас уже есть эта роль.```")
        elif value == 4:
            user_test = int(user_cookies) - role_four_cost
            if user_test > 0:
                await ctx.send("```🌻 Чтобы купить персональную роль, ввдите !buy_pr <название роли> <1-3(красный, голубой, зеленый)>.\n🌻 Администрация может удалить вашу роль без объяснения. Делайте нормальные названия.```")
            else:
                await ctx.send("🥀 Вам не хватает печенья!")
        elif value == 5:
            user_test = int(user_cookies) - role_four_cost
            if user_test > 0:
                await ctx.send("🌻 Чтобы купить мут пользователя, ввдите !buy_m <отметьте пользователя>.\n🌻 Мут выдается на время - 20 минут. Администрация может убрать мут без объяснений.")
            else:
                await ctx.send("```🥀 Вам не хватает печенья!```")
        elif value > 4:
            await ctx.send("```🥀 Данной позиции не существует.```")
        elif value <= 0:
            await ctx.send("```🥀 Данной позиции не существует.```")


    @buy.error
    async def buy_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🥀 Данная команда принимает значение в диапозоне от 1 до 3.```")



    @bot.command(pass_context=True)
    async def buy_pr(ctx, user_value: str, user_value_two: int):
        member = ctx.author

        step_one = db_select(ctx.author.id)
        step_two = step_one.split()[1]
        user_cookies = step_two.replace(",", "")
        user_test = int(user_cookies) - role_four_cost
        if user_test > 0:
            role = str(user_value)
            guild = ctx.guild
            if user_value_two == 1:
                await guild.create_role(name=role, colour=discord.Colour(0xFF0000))
                role_add = discord.utils.get(ctx.guild.roles, name=f"{role}")
                await member.add_roles(role_add)
            if user_value_two == 2:
                await guild.create_role(name=role, colour=discord.Colour(0x00E5FF))
                role_add = discord.utils.get(ctx.guild.roles, name=f"{role}")
                await member.add_roles(role_add)
            if user_value_two == 3:
                await guild.create_role(name=role, colour=discord.Colour(0x00FF55))
                role_add = discord.utils.get(ctx.guild.roles, name=f"{role}")
                await member.add_roles(role_add)
            await ctx.send(f"```🌻 Поздравляю, вы успешно купили роль {role}! Администрация может удалить вашу роль без объяснения.```")
            logging.critical(
                Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} BOUGHT PERSONAL ROLE - {role}!")
            db_update_special_minus("cookies", ctx.author.id, "cookies", role_four_cost)

        else:
            await ctx.send("```🥀 Вам не хватает печенья!```")


    @buy_pr.error
    async def buy_pr_error(ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("```🥀 Ошибка! Название роли состоит из одного слова! Прим. - !buy 4.```")





    @bot.command(pass_context=True)
    async def buy_m(ctx, member: discord.Member = None):
        time = 1200
        step_one = db_select(ctx.author.id)
        step_two = step_one.split()[1]
        user_cookies = step_two.replace(",", "")
        user_test = int(user_cookies) - role_five_cost
        if user_test > 0:
            if not member:
                await ctx.send("```🥀 Выберите пользователя.```")
                return
            elif member:
                role = discord.utils.get(ctx.guild.roles, name="замучен")
                embed1 = discord.Embed(title=f"{member}",
                                       description=f"{member.mention} был замучен пользователем - {ctx.message.author.mention}.",
                                       color=0xff00f6)
                embed1.set_footer(text=f"{time_now}")
                await ctx.send(embed=embed1)
                await member.add_roles(role)
                db_update_special_minus("cookies", ctx.author.id, "cookies", role_five_cost)
                logging.critical(Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} BOUGHT USER {member.display_name} MUTE!")
                await asyncio.create_task(shop_unmute_task(ctx, member, role, time))
                await ctx.send(
                    f"{member.mention} был размучен.\n\nСрок блокировки - {time}.\n\nПользователем - {ctx.message.author.mention}.",
                    color=0xff00f6)


        else:
            await ctx.send("```🥀 Вам не хватает печенья!```")





    async def shop_unmute_task(ctx, member, role, time):
        await asyncio.sleep(time)
        await member.remove_roles(role)


    @buy_m.error
    async def buy_m_error(ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("```🥀 Ошибка! Название роли состоит из одного слова! Прим. - !buy_r 4.```")







    @bot.command()
    async def start_r(ctx, value: int):
        role = discord.utils.get(ctx.guild.roles, name="bad guy")
        role2 = discord.utils.get(ctx.guild.roles, name="hey bruh")
        role3 = discord.utils.get(ctx.guild.roles, name="микрочелик")
        if role in ctx.author.roles:
            await ctx.send("```🥀 У вас уже есть начальная роль!```")
        elif role2 in ctx.author.roles:
            await ctx.send("```🥀 У вас уже есть начальная роль!```")
        elif role3 in ctx.author.roles:
            await ctx.send("```🥀 У вас уже есть начальная роль!```")
        elif role and role2 and role3 not in ctx.author.roles:
            member = ctx.author
            if value == 1:
                await member.add_roles(role)
                await ctx.send("```🌻 Вы успешно получили роль bad guy!```")
            elif value == 2:
                await member.add_roles(role)
                await ctx.send("```🌻 Вы успешно получили роль hey bruh!```")
            elif value == 3:
                await member.add_roles(role)
                await ctx.send("```🌻 Вы успешно получили роль микрочелик!```")
            elif value > 3:
                await ctx.send("```🥀 Данной позиции не существует.```")
            elif value <= 0:
                await ctx.send("```🥀 Данной позиции не существует.```")


    @start_r.error
    async def start_r_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🥀 Данная команда принимает значение в диапозоне от 1 до 3.```")




    @bot.command()
    async def color(ctx, value: int):
        color1 = discord.utils.get(ctx.guild.roles, name="pink")
        color2 = discord.utils.get(ctx.guild.roles, name="green")
        color3 = discord.utils.get(ctx.guild.roles, name="black")
        color4 = discord.utils.get(ctx.guild.roles, name="yellow")
        color5 = discord.utils.get(ctx.guild.roles, name="red")
        color6 = discord.utils.get(ctx.guild.roles, name="blue")

        member_user = ctx.author
        if value == 1:
            await member_user.add_roles(color1)
            await member_user.remove_roles(color2,color3,color4,color5,color6)
        elif value == 2:
            await member_user.add_roles(color2)
            await member_user.remove_roles(color1, color3, color4, color5, color6)
        elif value == 3:
            await member_user.add_roles(color3)
            await member_user.remove_roles(color2, color1, color4, color5, color6)
        elif value == 4:
            await member_user.add_roles(color4)
            await member_user.remove_roles(color2, color3, color1, color5, color6)
        elif value == 5:
            await member_user.add_roles(color5)
            await member_user.remove_roles(color2, color3, color4, color1, color6)
        elif value == 6:
            await member_user.add_roles(color6)
            await member_user.remove_roles(color2, color3, color4, color5, color1)
        elif value > 6:
            await ctx.send("```🥀 Данной позиции не существует.```")
        elif value <= 0:
            await ctx.send("```🥀 Данной позиции не существует.```")




    @color.error
    async def color_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("```🥀 Данная команда принимает значение в диапозоне от 1 до 6.```")



    @bot.command()
    async def bonus(ctx):
        step_one = db_select(ctx.author.id)
        step_two = step_one.split()[4]
        user_bonus = int(step_two.replace(",", ""))

        if user_bonus == 0:
            embed1 = discord.Embed(title=f"⭐️ Поздравляем!",
                                   description=f"🌻 Вы успешно получили бонус в размере 500 🍪!",
                                   color=0xff00f6)
            embed1.set_footer(text=f"{time_now}")
            await ctx.send(embed=embed1)
            db_update_special_plus("bonus", ctx.author.id, "bonus", 1)
            db_update_special_plus("cookies", ctx.author.id, "cookies", 500)
            logging.info(f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} TAKE BONUS")
            await asyncio.create_task(bonus_task(ctx))
        elif user_bonus == 1:
            await ctx.send("```🥀 Вы уже использовали бонус, подождите 12 часов перед повторным использованием команды!```")



    async def bonus_task(ctx):
        await asyncio.sleep(43200)
        db_update_special_minus("bonus", ctx.author.id, "bonus", 1)
        await ctx.send(
            f"{ctx.message.author.mention}```🌻 вы можете получить бонус! Для получения введите !bonus.```",)

    @bonus.error
    async def bonus_error(ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("```🥀 У вас нет своего рюкзака. Чтобы получить введите !get_bag.```")


    @bot.command()
    async def transfer(ctx,user_value: int, member: discord.Member = None):
        if not member:
            await ctx.send("🥀 Выберите пользователя.")
        elif member:
            step_one = db_select(ctx.author.id)
            step_two = step_one.split()[1]
            user_cookies = step_two.replace(",", "")
            user_test = int(user_cookies) - int(user_value)
            if user_test > 0:
                await ctx.send(
                    f"```🌻 {ctx.message.author.display_name} вы перевели {user_value} 🍪 пользователю {member.display_name}! Печенье возврату не подлежит!```", )
                db_update_special_plus("cookies", member.id, "cookies", user_value)
                db_update_special_minus("cookies", ctx.author.id, "cookies", user_value)
                logging.critical(
                    Fore.LIGHTGREEN_EX + f"{time_now} | NEW EVENT: USER {ctx.message.author.display_name} TRANSFER {user_value} COOKIES TO {member.display_name}!")
            elif user_test <= 0:
                await ctx.send("```🥀 У вас не хватает печенья.```")

    @transfer.error
    async def transfer_error(ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("```🥀 Введите количество печенья. Прим. - !transfer 500 <отметьте пользователя>.```")


    @bot.command()
    async def s_time(ctx):
        await ctx.send("```🌻 CHECK CONSOLE!```")
        print(Fore.LIGHTGREEN_EX + "--- %s seconds ---" % (time.time() - start_time))







    bot.run('DISCORD_TOKEN')

