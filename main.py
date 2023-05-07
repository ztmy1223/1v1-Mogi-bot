import discord
import aiohttp
import asyncio
from discord.ext import commands

Intents = discord.Intents.all()
bot = commands.Bot(command_prefix=";",
                   intents=Intents,
                   allowed_mentions=discord.AllowedMentions(everyone=True))


bot.remove_command("help")


@bot.event
async def on_ready():
  print("準備完了")

  try:
    synced = await bot.tree.sync()
    print(f"{len(synced)}個のコマンドを同期しました。")
  except Exception as e:
    print(e)


async def get_switchFc(session, url):
  try:
    async with session.get(url) as resp:
      player_data = await resp.json()
      if 'switchFc' in player_data.keys():
        return player_data['switchFc']
      else:
        return "You must present fc"
  except:
    return "fc could not be loaded"


@bot.tree.command(name="s")
async def start(interaction: discord.Interaction):
  c_list = [interaction.user.id]
  c_nick_list = [interaction.user.nick or interaction.user.name]
  message_list = []

  class Button_start(discord.ui.View):

    def __init__(self, *, timeout=600):
      super().__init__(timeout=timeout)
      self.cooldown = commands.CooldownMapping.from_cooldown(
        1, 30, commands.BucketType.category)

    @discord.ui.button(label="Can", style=discord.ButtonStyle.primary)
    async def button_can(self, button: discord.ui.Button,
                         interaction: discord.Interaction):
      if button.user.id != c_list[0]:
        bucket = self.cooldown.get_bucket(button.message)
        retry = bucket.update_rate_limit()
        if retry:
          await button.response.defer()
        else:
          await button.response.defer()
          await button.followup.delete_message(message_list[0])
          c_list.append(button.user.id)
          c_nick_list.append(button.user.nick or button.user.name)

          class Button_canhost(discord.ui.View):

            def __init__(self, *, timeout=600):
              super().__init__(timeout=timeout)
              self.cooldown = commands.CooldownMapping.from_cooldown(
        1, 30, commands.BucketType.category)

            @discord.ui.button(label="Can host",
                               style=discord.ButtonStyle.success)
            async def button_can(self, button: discord.ui.Button,
                                 interaction: discord.Interaction):
              if button.user.id in c_list:
                bucket = self.cooldown.get_bucket(button.message)
                retry = bucket.update_rate_limit()
                if retry:
                  await button.response.defer()
                else:
                  await button.response.defer()
                  await button.followup.delete_message(message_list[1])
                  async with aiohttp.ClientSession() as session:
                      url = f'https://www.mk8dx-lounge.com/api/player?discordId={button.user.id}'
                      fc_list = [asyncio.ensure_future(get_switchFc(session, url))]
                      fclist = await asyncio.gather(*fc_list)
                      embedfc = discord.Embed(
                        title=f"Host: {button.user.nick or button.user.name}",
                        color=0xffffff)
                      embedfc.add_field(name=fclist[0], value="")
                      await button.followup.send(
                        content=
                        f"<@{c_list[0]}> <@{c_list[1]}>\nYour in-game name must be your MK1 lounge name (exactly as registered)\nGood Luck!",
                        embed=embedfc)
                      await button.followup.send(
                        f'!submit tier\n"{c_nick_list[0]}" 0\n"{c_nick_list[1]}" 0')
    
              else:
                await button.response.defer()

          host_message = await button.followup.send(
            content=
            f"<@{c_list[0]}> <@{c_list[1]}> 1v1 mogi has 2 players\nIf you can host, press the button below",
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
          await button.response.defer()
          await button.followup.delete_message(message_list[0])
          await button.followup.send(
            content=f"{button.user.mention} has ended mogi")
      else:
        await button.response.defer()


    # @discord.ui.button(label="@Tags", style=discord.ButtonStyle.secondary)
    # async def button_tags(self, button: discord.ui.Button,
    #                       interaction: discord.Interaction):
    #   if button.user.id == c_list[0]:
    #     bucket = self.cooldown.get_bucket(button.message)
    #     retry = bucket.update_rate_limit()
    #     if retry:
    #       await button.response.defer()
    #     else:
    #       await button.response.send_message(f"<@&{1084751516168093787}>")
    #   else:
    #     await button.response.defer()

  await interaction.response.send_message(
    content=
    f"{interaction.user.mention} has started a 1v1 mogi\nPress the Can button below to join the 1v1 mogi",
    view=Button_start(),
    delete_after=600)
  start_message = await interaction.original_response()
  message_list.append(start_message.id)


@bot.tree.command(name="end")
async def end(interaction: discord.Interaction):
  await interaction.response.send_message(f"{interaction.user.mention} has ended mogi")


bot.run('token')
