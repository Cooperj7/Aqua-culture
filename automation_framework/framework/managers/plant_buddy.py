import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage

import framework.managers.email as email

from framework.database.database import select_data, ResultCount, _execute_query, path_to_database
from framework.io.io import IoType, Io




class PlantBuddy(Io):

    def __init__(self, name: str, actions, sender_email, sender_password, receiving_emails, zipcode, phone_num):

        super().__init__(name, IoType.OUTPUT, actions, [])

        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiving_emails = receiving_emails
        self.zipcode = zipcode
        self.phone_num = phone_num

        self.zone = "-99a"
        self.zone = _execute_query(path_to_database, f"SELECT zone FROM zipcode_to_zone WHERE zipcode LIKE '{zipcode}'", ResultCount.ONE)[0]


    def check_date(self):

        season_starts = {"start_seeds": [32, "last_frost"], "last_frost_warning": [7, "last_frost"],
                         "first_frost_warning": [21, "first_frost"]}

        start_seeds_msg = "It is about 8 weeks before your last expected frost date. Now is the time to start seeds indoors if " \
                          "possible."
        last_frost_msg = "The last frost for your area should be in a week from now. Get ready to move seedlings started indoors" \
                         "outside or to sow seeds outdoors."
        first_frost_msg = "The first expected frost is in 3 weeks. Consider moving plants that are not frost hardy indoors soon."
        messages = {"start_seeds": start_seeds_msg, "first_frost": first_frost_msg, "last_frost": last_frost_msg}

        found_date = datetime.now()
        found_date.strftime("%m-%d-%Y")
        for key in season_starts:
            date_string = select_data("frost_dates", ResultCount.ONE, [season_starts[key][1]],
                                      where=f"zone LIKE '{self.zone}'")
            found_date = found_date.strptime(date_string[0], "%m-%d-%Y") - timedelta(days=season_starts[key][0])

            check_date = datetime.now()
            if check_date.year == found_date.year and check_date.month == found_date.month and check_date.day == found_date.day:
                self._send_email(email.EmailReasons.PLANT_BUDDY, messages[key], self.sender_email, self.sender_password, self.receiving_emails)

    def _send_email(self, alert_type: email.EmailReasons, message_text: str, sender_email, sender_password,
                    receiving_emails):
        """
        Sends an alert message to the given email address.

        :param alert_type: Type of alert being sent ex. "HIGH-ALERT-VALUE"
        :param message_text: Text to be sent in the message
        :return: None
        """

        ssl_port = 465  # For SSL

        try:
            # Create a secure SSL context
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", ssl_port, context=context) as server:
                server.login(sender_email, sender_password)

                for email in receiving_emails:
                    message_body = message_text

                    receiver_email = email

                    email_message = EmailMessage()
                    email_message.set_content(message_body)
                    email_message['Subject'] = f'{alert_type.value}'
                    email_message['From'] = sender_email
                    email_message['To'] = receiver_email

                    server.send_message(email_message)

        except:
            log.getLogger().critical(f"Failed to send email using")

    def update_from_database(self):

        temp_zipcode = select_data("Settings", ResultCount.ONE, columns=["Value"], where="Setting_name LIKE 'zipcode'")
        if self.zipcode != temp_zipcode:
            self.zipcode = temp_zipcode
            self.zone = _execute_query(path_to_database, f"SELECT zone FROM zipcode_to_zone WHERE zipcode LIKE '{zipcode}'", ResultCount.ONE)[0]

        temp_phone_num = select_data("Settings", ResultCount.ONE, columns=["Value"], where="Setting_name LIKE 'phone_num'")
        if self.phone_num != temp_phone_num:
            self.phone_num = temp_phone_num