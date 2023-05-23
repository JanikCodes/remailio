import mysql.connector

import config
from Classes.reminder import Reminder


class Database():
    
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host=config.botConfig["host"],
            user=config.botConfig["user"],
            password=config.botConfig["password"],
            port=config.botConfig["port"],
            database=config.botConfig["database"],
            charset='utf8mb4'
        )
        self.cursor = self.mydb.cursor()

        # Check if the connection is alive
        if self.mydb.is_connected():
            print("Database connection successful")
        else:
            print("Database connection failed")

    def add_new_reminder(self, reminder):
        sql = f'INSERT INTO reminder VALUE(NULL, "{reminder.get_header()}", "{reminder.get_content()}", "{reminder.get_emails_formatted_sql()}", %s, %s);'
        formatted_sql = sql.strip().replace('"', '\"')
        values = (reminder.get_date_formatted_sql(), reminder.get_time_formatted_sql())
        self.cursor.execute(formatted_sql, values)
        self.mydb.commit()

    def get_all_expired_reminders(self):
        reminders = []

        sql = f'select idReminder, header, content, emails from reminder where date < CURDATE() or (date = CURDATE() AND time < CURTIME());'
        formatted_sql = sql.strip().replace('"', '\"')

        self.cursor.execute(formatted_sql)
        res = self.cursor.fetchall()
        if res:
            for row in res:
                reminder = Reminder()
                reminder.set_id(row[0])
                reminder.set_header(row[1])
                reminder.set_content(row[2])
                reminder.set_emails(row[3])
                reminders.append(reminder)

        return reminders


    def remove_reminder(self, idReminder):
        sql = f"DELETE FROM reminder WHERE idReminder = {idReminder};"
        self.cursor.execute(sql)
        self.mydb.commit()