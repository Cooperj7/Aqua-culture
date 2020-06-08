import smtplib
import ssl
from email.message import EmailMessage
from enum import Enum
import logging as log

from framework.time.timer import Timer


class EmailReasons(Enum):
    ERROR = "ERROR"
    HIGH_VALUE = "HIGH-VALUE-ALERT"
    LOW_VALUE = "LOW-VALUE-ALERT"


class EmailController:

    def __init__(self, sender_email: str, sender_password: str, receiving_emails: list):
        """
        Used to send email/text notifications.

        :param sender_email: Email address that is sending the email
        :param sender_password: The password used to login to the sender email
        :param receiving_emails: A list of emails or phone numbers to send messages to
        :return: None
        """

        self.sender_email = sender_email
        self.sender_password = sender_password

        self.receiving_emails = receiving_emails

        self.message_type_timers = {}

    def check_timer(self, sensor_name: str, alert_type: EmailReasons) -> bool:
        """
        Sets a timer for each type of notification being sent. This avoids being spamming messages. Timers are set by
        sensor name and alert type. This is so timers do no collide.

        :param sensor_name: Name of the sensor sending the alert
        :param alert_type: Type of alert being sent ex. "HIGH-VALUE-ALERT"
        :return: None
        """

        if sensor_name not in self.message_type_timers.keys():
            self.message_type_timers[sensor_name] = {}

        if alert_type not in self.message_type_timers[sensor_name].keys():
            self.message_type_timers[sensor_name][alert_type] = Timer(alert_type.value, 300)

        return self.message_type_timers[sensor_name][alert_type].check_time()

    def send_email(self, sensor_name: str, alert_type: EmailReasons, message_text: str):
        """
        Sends an email message to the addresses stored in receiving_emails.

        :param sensor_name: Name of sensor sending the alert
        :param alert_type: Type of alert being sent ex. "HIGH-ALERT-VALUE"
        :param message_text: Text to be sent in the message
        :return: None
        """

        result = self.check_timer(sensor_name, alert_type)
        if result:

            self._send_email(alert_type, message_text)

    def _send_email(self, alert_type: EmailReasons, message_text: str):
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
                server.login(self.sender_email, self.sender_password)

                for email in self.receiving_emails:

                    message_body = message_text

                    receiver_email = email

                    email_message = EmailMessage()
                    email_message.set_content(message_body)
                    email_message['Subject'] = f'{alert_type.value}'
                    email_message['From'] = self.sender_email
                    email_message['To'] = receiver_email

                    server.send_message(email_message)

        except:
            log.getLogger().critical(f"Failed to send email using")
