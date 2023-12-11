import discord
import aiosqlite
import mysql.connector
from time import time
from discord.ext import commands, tasks

db_name = 'mogilist.sqlite'

add_mogi = 'INSERT INTO mogilist (player_id, channel_id, time, message_id) VALUES (?,?,?,?)'
get_mogi = 'SELECT * FROM mogilist WHERE time = ?;'
get_all = 'SELECT * FROM mogilist;'
delete_mogilist = 'DELETE FROM mogilist;'
delete_mogi = 'DELETE FROM mogilist WHERE time = ?;'

host = 'host'
user = 'user'
password = 'password'
database = 'database'

mydb = mysql.connector.connect(host=host,
                               user=user,
                               password=password,
                               database=database)
mycursor = mydb.cursor()

Intents = discord.Intents.all()
bot = commands.Bot(command_prefix=";",
                   intents=Intents,
                   allowed_mentions=discord.AllowedMentions(everyone=True))

bot.remove_command("help")


# mogilist
@tasks.loop(seconds=60)
async def um():
  channel = bot.get_channel(1142846630954016918)
  message = await channel.fetch_message(1142847916487225425)
  async with aiosqlite.connect(db_name) as db:
    async with db.execute(get_all) as cur:
      mogi_list = await cur.fetchall()
      t = time()
      content = "<MK1 mogilist>"
      for mogi in mogi_list:
        if t - mogi[2] > 600:
          await db.execute(delete_mogi, (mogi[2],))
          await db.commit()
        else:
          mogi_channel = bot.get_channel(mogi[1])
          content = content + "\n" + mogi_channel.mention
      content = content + f"\nLast updated: <t:{int(t)}:T>\nThis will update every 60 seconds."
      await message.edit(content=content)

mute = 0

@bot.event
async def on_ready():
  print("準備完了")

  try:
    if mydb.is_connected():
      print("MySQLデータベースに接続されました。")
    synced = await bot.tree.sync()
    print(f"{len(synced)}個のコマンドを同期しました。")
    guild = discord.utils.find(lambda g: g.id == 1081858313454637066,
                               bot.guilds)
    global mute
    mute = guild.get_role(1143183036389785610)
    print(mute)
    um.start()
  except Exception as e:
    print(e)
  async with aiosqlite.connect(db_name) as db:
    async with db.execute(get_all) as cur:
      mogi_list = await cur.fetchall()
      for mogi in mogi_list:
        mogi_channel = bot.get_channel(mogi[1])
        old_message = await mogi_channel.fetch_message(mogi[3])
        await old_message.delete()
    await db.execute(delete_mogilist)
    await db.commit()
    print("Successful")

async def get_switchFc(discordId):
  global mydb, mycursor
  try:
    mydb.commit()
    mycursor.execute('SELECT switchFc FROM player_info WHERE discordId = %s;',
                   (discordId, ))
  except:
    mydb = mysql.connector.connect(host=host,
                               user=user,
                               password=password,
                               database=database)
    mycursor = mydb.cursor()
    mydb.commit()
    mycursor.execute('SELECT switchFc FROM player_info WHERE discordId = %s;',
                   (discordId, ))
  fc = mycursor.fetchall()
  if mycursor.rowcount == 1:
    return fc[0][0]
  else:
    return "Error"
    
async def check_player(discordId):
  global mydb, mycursor
  try:
    mydb.commit()
    mycursor.execute('SELECT name FROM player_info WHERE discordId = %s;',
                   (discordId, ))
  except:
    mydb = mysql.connector.connect(host=host,
                               user=user,
                               password=password,
                               database=database)
    mycursor = mydb.cursor()
    mydb.commit()
    mycursor.execute('SELECT name FROM player_info WHERE discordId = %s;',
                   (discordId, ))
  name = mycursor.fetchall()
  if mycursor.rowcount == 1:
    return name[0][0]
  else:
    return False

# /s
@bot.tree.command(name="s")
async def start(interaction: discord.Interaction):
  starter = await check_player(interaction.user.id)
  if starter != False:
    c_list = [interaction.user.id]
    c_nick_list = [starter]
    t = time()
    # async with aiosqlite.connect(db_name) as db:
    #   await db.execute(add_mogi, (interaction.user.id, interaction.channel.id, t))
    #   await db.commit()
    message_list = []
  
    class Button_start(discord.ui.View):
  
      def __init__(self, *, timeout=600):
        super().__init__(timeout=timeout)
        self.cooldown = commands.CooldownMapping.from_cooldown(
          1, 30, commands.BucketType.category)
  
      @discord.ui.button(label="Can", style=discord.ButtonStyle.primary)
      async def button_can(self, button: discord.ui.Button,
                           interaction: discord.Interaction):
        if mute in button.user.roles:
          await button.response.defer()
        else:
          if button.user.id != c_list[0]:
            participant = await check_player(button.user.id)
            if participant != False:
              bucket = self.cooldown.get_bucket(button.message)
              retry = bucket.update_rate_limit()
              if retry:
                await button.response.defer()
              else:
                c_list.append(button.user.id)
                c_nick_list.append(participant)
                async with aiosqlite.connect(db_name) as db:
                  await db.execute(delete_mogi, (t,))
                  await db.commit()
                await button.response.defer()
                await button.followup.delete_message(message_list[0])
      
                class Button_canhost(discord.ui.View):
      
                  def __init__(self, *, timeout=600):
                    super().__init__(timeout=timeout)
                    self.cooldown = commands.CooldownMapping.from_cooldown(
              1, 30, commands.BucketType.category)
      
                  @discord.ui.button(label="Can host",
                                     style=discord.ButtonStyle.success)
                  async def button_can(self, button: discord.ui.Button,
                                       interaction: discord.Interaction):
                    if mute in button.user.roles:
                      await button.response.defer()
                    else:
                      if button.user.id in c_list:
                        bucket = self.cooldown.get_bucket(button.message)
                        retry = bucket.update_rate_limit()
                        if retry:
                          await button.response.defer()
                        else:
                          await button.response.defer()
                          await button.followup.delete_message(message_list[1])
                          # fc = await get_switchFc(button.user.id)
                          if button.user.id == c_list[0]:
                            host = c_nick_list[0]
                          else:
                            host = c_nick_list[1]
                          embedfc = discord.Embed(
                            title=f"Host: {host}",
                            color=0xffffff)
                          # embedfc.add_field(name=fc, value="")
                          await button.followup.send(
                            content=
                            f"<@!{c_list[0]}> <@!{c_list[1]}>\nYour in-game name must be your MK1 lounge name (exactly as registered)\nGood Luck!",
                            embed=embedfc)
                          await button.followup.send(
                            f'!submit tier\n{c_nick_list[0]} 0\n{c_nick_list[1]} 0')
            
                      else:
                        await button.response.defer()
      
                host_message = await button.followup.send(
                  content=
                  f"<@!{c_list[0]}> <@!{c_list[1]}> 1v1 mogi has 2 players\nIf you can host, press the button below",
                  view=Button_canhost())
                message_list.append(host_message.id)
      
          else:
            await button.response.defer()
  
      @discord.ui.button(label="End", style=discord.ButtonStyle.danger)
      async def button_end(self, button: discord.ui.Button,
                           interaction: discord.Interaction):
  
        if button.user.id == c_list[0]:
          bucket = self.cooldown.get_bucket(button.message)
          retry = bucket.update_rate_limit()
          if retry:
            await button.response.defer()
          else:
            async with aiosqlite.connect(db_name) as db:
              await db.execute(delete_mogi, (t,))
              await db.commit()
            await button.response.defer()
            await button.followup.delete_message(message_list[0])
            await button.followup.send(
              content=f"<@!{c_list[0]}> has ended mogi")
        else:
          await button.response.defer()
  
    await interaction.response.send_message(
      content=
      f"<@!{c_list[0]}> has started a 1v1 mogi\nPress the Can button below to join the 1v1 mogi\nThis message is automatically deleted after 10 minutes",
      view=Button_start(),
      delete_after=600)
    start_message = await interaction.original_response()
    message_list.append(start_message.id)
    async with aiosqlite.connect(db_name) as db:
      await db.execute(add_mogi, (interaction.user.id, interaction.channel.id, t, start_message.id))
      await db.commit()


@bot.tree.command(name="end")
async def end(interaction: discord.Interaction):
  await interaction.response.send_message(f"<@!{interaction.user.id}> has ended mogi")


bot.run('token')
