from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

from Classes.reminder import Reminder


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

            reminder = Reminder()
            reminder.set_date(final_date)
            reminder.set_time(final_time)
            reminder.set_emails(e_mails)

        except ValueError as e:
            error_embed = discord.Embed(title="Invalid Input", description=f"Please write the date in this format:\n`day.month.year` and the time `hour:minute`", color=discord.Color.red())
            return await interaction.response.send_message(embed=error_embed)

        await interaction.response.send_modal(RemindContentModal(db=self.db, reminder=reminder))

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
    def __init__(self, db, reminder):
        super().__init__(label=f"Yes", style=discord.ButtonStyle.green)
        self.db = db
        self.reminder = reminder

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        message = interaction.message
        edited_embed = message.embeds[0]
        edited_embed.colour = discord.Color.green()

        self.db.add_new_reminder(reminder=self.reminder)
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
    def __init__(self, db, reminder):
        super().__init__(timeout=None)
        self.add_item(AcceptButton(db=db, reminder=reminder))
        self.add_item(DeclineButton())

class RemindContentModal(discord.ui.Modal):
    header = discord.ui.TextInput(label='Title')
    content = discord.ui.TextInput(label='Content', style=discord.TextStyle.paragraph)

    def __init__(self, db, reminder):
        super().__init__(title="Reminder Content")
        self.db = db
        self.reminder = reminder

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        self.reminder.set_header(self.header.value)
        self.reminder.set_content(self.content.value)

        embed = discord.Embed(title=f"Alright!",
                              description=f"I'll remind you on the **{self.reminder.get_date_formatted()}** at **{self.reminder.get_time_formatted()}** o clock.\n Does this sound good?",
                              colour=discord.Color.green())
        embed.add_field(name="Title", value=self.reminder.get_header(), inline=False)
        embed.add_field(name="Content", value=self.reminder.get_content(), inline=False)
        embed.set_footer(text=f"E-Mails: {self.reminder.get_emails_for_display()}")

        await interaction.followup.send(embed=embed, view=RemindMeReviewView(db=self.db, reminder=self.reminder))

