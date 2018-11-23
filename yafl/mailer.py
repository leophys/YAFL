# coding: utf-8
from email.mime.text import MIMEText
import logging
import queue
import smtplib
import sys
import threading


local_logger = logging.getLogger(__name__)


class Mailer(threading.Thread):
    def __init__(self,
                 queue: queue.Queue,
                 address: str,
                 username: str,
                 password: str,
                 from_field: str,
                 to_field: str,
                 starttls: bool = None,
                 port: int = 25,
                 logger: logging.Logger = None,
                 *args, **kwargs,
                 ):
        """
        An helper class to send emails to warn about bruteforce
        attempts.
        """
        super().__init__(*args, **kwargs)
        self.address = address
        self.username = username
        self.password = password
        self.from_field = from_field
        self.to_field = to_field
        self.starttls = starttls
        self.port = port
        self.queue = queue
        self._stop = threading.Event()
        if logger:
            self.logger = logger
        else:
            self.logger = local_logger
        self.logger.info("Mailer init'd.")
        self.logger.debug("Mailer parameters: %r", self)

    def __repr__(self):
        r = "<Mailer (address: {address!s}:{port!s}, "\
            "username: {username!s}, "\
            "password: ********, "\
            "from: {from_field!s}, "\
            "to: {to_field!s}, "\
            "starttls: {starttls!s})>"
        return r.format(
            address=self.address,
            port=self.port,
            username=self.username,
            from_field=self.from_field,
            to_field=self.to_field,
            starttls=self.starttls
        )

    def stop(self):
        """
        Stop the thread gracefully.
        """
        self.logger.info("Stopping mailer.")
        self._stop.set()

    def is_stopped(self):
        """
        Check if the thread is stopped.
        """
        return self._stop.is_set()

    def connect(self):
        """
        Connect to the server using the credentials provided
        at initialization.
        """
        server = smtplib.SMTP(self.address, self.port)
        self.logger.debug("Connected to: %s:%d", self.address, self.port)
        if self.starttls:
            server.starttls()
            self.logger.debug("STARTTLS done")
        return server

    def send_message(self, subject: str, message: str):
        """
        Sends a message and closes the connection.
        """
        message = MIMEText(trim(message))
        message['Subject'] = subject
        message['From'] = self.from_field
        message['To'] = self.to_field
        self.logger.debug("Sending message: %s", message)
        server = self.connect()
        server.send_message(message)
        self.logger.debug("Message sent.")
        server.quit()

    def run(self):
        """
        The target method for self.start()
        """
        while not self.is_stopped():
            subject, message = self.queue.get()
            self.logger.info("Sending mail: %s", subject)
            self.send_message(subject, message)


def trim(string: str):
    """From:
    https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    """
    if not string:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = string.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)
