from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands


class RemindMeCommand(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.db = client.database

    @app_commands.describe(
        e_mails="Enter E-Mails, separated by ,",
    )
    @app_commands.rename(e_mails='e-mails')
    @app_commands.command(name="remindme", description="Set an E-Mail reminder!")
    async def clear(self, interaction: discord.Interaction, e_mails: str, date: str, time: str):
        if not interaction or interaction.is_expired():
            return

        try:
            final_date = self.parse_string_date(date)
            final_time = self.parse_string_time(time)
        except ValueError as e:
            error_embed = discord.Embed(title="Invalid Input", description=f"Please write the date in this format:\n`day.month.year` and the time `hour:minute`", color=discord.Color.red())
            return await interaction.response.send_message(embed=error_embed)

        await interaction.response.send_modal(RemindContentModal(db=self.db, final_date=final_date, final_time=final_time, e_mails=e_mails))

    def parse_string_date(self, string_date):
        datetime_obj = datetime.strptime(string_date, "%d.%m.%Y")
        date_obj = datetime_obj.date()
        return date_obj

    def parse_string_time(self, string_time):
        datetime_obj = datetime.strptime(string_time, "%H:%M")
        time_obj = datetime_obj.time()
        return time_obj

async def setup(client: commands.Bot) -> None:
    await client.add_cog(RemindMeCommand(client))


class AcceptButton(discord.ui.Button):
    def __init__(self, db, final_date, final_time, e_mails, header, content):
        super().__init__(label=f"Yes", style=discord.ButtonStyle.green)
        self.db = db
        self.final_date = final_date
        self.final_time = final_time
        self.e_mails = e_mails
        self.header = header
        self.content = content

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        message = interaction.message
        edited_embed = message.embeds[0]
        edited_embed.colour = discord.Color.green()

        self.db.add_new_reminder(self.final_date, self.final_time, self.e_mails, self.header, self.content)
        print("Success!")
        await interaction.message.edit(embed=edited_embed, view=None, delete_after=3)

class DeclineButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label=f"Cancel", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        message = interaction.message
        edited_embed = message.embeds[0]
        edited_embed.colour = discord.Color.red()

        await interaction.message.edit(embed=edited_embed, view=None, delete_after=3)

class RemindMeReviewView(discord.ui.View):
    def __init__(self, db, final_date, final_time, e_mails, header, content):
        super().__init__(timeout=None)
        self.add_item(AcceptButton(db=db, final_date=final_date, final_time=final_time, e_mails=e_mails, header=header, content=content))
        self.add_item(DeclineButton())

class RemindContentModal(discord.ui.Modal):
    header = discord.ui.TextInput(label='Title')
    content = discord.ui.TextInput(label='Content', style=discord.TextStyle.paragraph)

    def __init__(self, db, final_date, final_time, e_mails):
        super().__init__(title="Reminder Content")
        self.db = db
        self.final_date = final_date
        self.final_time = final_time
        self.e_mails = e_mails

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        email_str = str()
        email_tuple = self.e_mails.split(",")
        for mail in email_tuple:
            email_str += f" {mail}"

        embed = discord.Embed(title=f"Alright!",
                              description=f"I'll remind you on the **{self.final_date.strftime('%d.%m.%Y')}** at **{self.final_time.strftime('%H:%M')}** o clock.\n Does this sound good?",
                              colour=discord.Color.green())
        embed.add_field(name="Title", value=self.header.value, inline=False)
        embed.add_field(name="Content", value=self.content.value, inline=False)
        embed.set_footer(text=f"E-Mails: {email_str}")

        await interaction.followup.send(embed=embed, view=RemindMeReviewView(db=self.db, final_date=self.final_date, final_time=self.final_time, e_mails=self.e_mails, header=self.header, content=self.content))

