import logging
import os
import platform
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import discord
from colorama import Back, Fore, Style
from discord.ext import commands, tasks

import config
import db

MY_GUILD = discord.Object(id=763425801391308901)

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/=?!.', intents=discord.Intents().default())
        self.database = db.Database()

    async def setup_hook(self):
        for fileName in os.listdir('./Commands'):
            if fileName.endswith('.py'):
                extension = f'Commands.{fileName[:-3]}'
                await self.load_extension(extension)

        await self.tree.sync()

    async def on_ready(self):
        prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(f"{prfx} Logged in as {Fore.YELLOW} {self.user.name}")
        print(f"{prfx} Bot ID {Fore.YELLOW} {str(self.user.id)}")
        print(f"{prfx} Discord Version {Fore.YELLOW} {discord.__version__}")
        print(f"{prfx} Python Version {Fore.YELLOW} {str(platform.python_version())}")

        logging.warning("Now logging..")

        self.check_reminder.start()

    @tasks.loop(seconds=10)
    async def check_reminder(self):

        reminders = self.database.get_all_expired_reminders()

        # idReminder, header, content, emails
        for reminder in reminders:
            print("Send Reminder out!")
            # loop over emails
            emails = reminder.get_emails_formatted_sql().split('#')
            for email in emails:
                await self.send_email(config.botConfig["email_username"], config.botConfig["email_password"], email, reminder.get_header(), reminder.get_content())

            self.database.remove_reminder(idReminder=reminder.get_id())

    async def send_email(self, sender_email, sender_password, receiver_email, subject, message):
        smtp_server = 'mail.gmx.com'
        smtp_port = 587

        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach the message to the MIMEMultipart object
        msg.attach(MIMEText(message, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()

                # Login to the email account
                smtp.login(sender_email, sender_password)

                # Send the email
                smtp.send_message(msg)
        except Exception as e:
            print(f"Error while sending E-Mail.. {str(e)}")

client = Client()
client.run(config.botConfig["token"])