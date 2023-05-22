import mysql.connector

import config

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

    def add_new_reminder(self, final_date, final_time, e_mails, header,content):
        new_emails = e_mails.replace(",", "#")
        formatted_time = final_time.strftime("%H:%M:%S")
        formatted_date = final_date.strftime("%Y-%m-%d")

        sql = f'INSERT INTO reminder VALUE(NULL, "{header}", "{content}", "{new_emails}", %s, %s);'
        formatted_sql = sql.strip().replace('"', '\"')
        values = (formatted_date, formatted_time)
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
                reminders.append([row[0], row[1], row[2], row[3]])

        return reminders


    def remove_reminder(self, idReminder):
        sql = f"DELETE FROM reminder WHERE idReminder = {idReminder};"
        self.cursor.execute(sql)
        self.mydb.commit()