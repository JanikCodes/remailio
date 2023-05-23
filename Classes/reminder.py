
class Reminder:
    def __init__(self, id=None):
        if id:
            self.__id = id
            self.__emails = None
            self.__date = None
            self.__time = None
            self.__header = None
            self.__content = None
        else:
            # empty
            pass

    def set_id(self, id):
        self.__id = id

    def set_header(self, header):
        self.__header = header

    def set_content(self, content):
        self.__content = content

    def set_emails(self, emails):
        self.__emails = emails

    def set_time(self, time):
        self.__time = time

    def set_date(self, date):
        self.__date = date

    def get_id(self):
        return self.__id

    def get_header(self):
        return self.__header

    def get_content(self):
        return self.__content

    def get_time_formatted(self):
        return self.__time.strftime('%H:%M')

    def get_time_formatted_sql(self):
        return self.__time.strftime('%H:%M:%S')

    def get_date_formatted(self):
        return self.__time.strftime('%d.%m.%Y')

    def get_date_formatted_sql(self):
        return self.__time.strftime('%Y-%m-%d')

    def get_emails_for_display(self):
        email_str = str()
        email_tuple = self.__emails.split(",")
        for mail in email_tuple:
            email_str += f" {mail}"

        return email_str

    def get_emails_formatted_sql(self):
        return self.__emails.replace(",", "#")