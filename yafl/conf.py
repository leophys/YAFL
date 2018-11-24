# -*- encoding: utf-8 -*-
"""
This module provides the configuration facility for YAFL.

Given a configuration parameter, the order in which it is
processed is the following:
    - An environment variable (prefixed by 'YAFL_') al caps
    - The value of the parameter in a configuration file
    - A default value, included in this file
The order in which the configuration files are searched is:
    - $PWD/.yafl.{yaml,yml}
    - ~/.yafl.{yaml,yml}
    - /etc/yafl.{yaml,yml}
    - The path to a file in the environment variable YAFL_CONF_PATH
"""

import datetime
import logging
import os
import re

import click
import yaml


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


_NOW = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S")


_CONFIG_PATHS = (
    os.path.join(os.curdir, '.yafl.yaml'),
    os.path.join(os.curdir, '.yafl.yml'),
    os.path.join(os.path.expanduser('~'), '.yafl.yaml'),
    os.path.join(os.path.expanduser('~'), '.yafl.yml'),
    '/etc/yafl.yaml',
    '/etc/yafl.yml',
    os.environ.get('YAFL_CONF_PATH'),
)


DEFAULT_APP_CONF = {
    'db_path': '/tmp/yafl_%s.json' % _NOW,
    'log_level': logging.INFO,
    'address': '127.0.0.1',
    'port': 8081,
}


DEFAULT_MAIL_CONF = {
    'address': None,
    'port': 25,
    'username': None,
    'password': None,
    'from_field': None,
    'to_field': None,
    'starttls': None,
    'event_timeout': None,
}


def load_from_file(filepath: str = None) -> dict:
    conf = {}
    if filepath is not None:
        with open(filepath) as cf:
            conf = yaml.safe_load(cf)
        return conf
    for config_path in _CONFIG_PATHS:
        try:
            if config_path is not None:
                with open(config_path) as cf:
                    conf = yaml.safe_load(cf)
        except IOError:
            pass
    return conf


def read_section(conf: dict, section: str, default: dict) -> dict:
    """
    Composes a section of the conf dictionary. Follows the order:
        - env variable
        - configuration file
        - default
    Returns the specified section only.
    """
    secconf = {}
    for k in default.items():
        env_var = 'YAFL_{section}_{key}'.format(
            section=section.upper(), key=k[0].upper()
        )
        if env_var in os.environ.keys():
            secconf[k[0]] = os.environ.get(env_var)
        else:
            try:
                secconf[k[0]] = conf[section][k[0]]
            except KeyError:
                secconf[k[0]] = default[k[0]]
    return secconf


def cast_to_int(value: str) -> int:
    """
    Casts to int. Casts the empty string to 0.
    """
    if value == '':
        return 0
    return int(value)


def parse_timeout(timeout: str) -> datetime.timedelta:
    """
    Given an input string with units, outputs a corresponding timedelta
    object. If units missing, defaults to seconds.
    Accepted units are 's' (seconds), 'm' (minutes), 'h' (hours), 'd' (days).
    """
    res = re.match('^(\d*)d?(\d*)h?(\d*)m?(\d*)s?$', timeout, re.X)
    days, hours, minutes, seconds = res.groups()
    return datetime.timedelta(
        days=cast_to_int(days),
        hours=cast_to_int(hours),
        minutes=cast_to_int(minutes),
        seconds=cast_to_int(seconds)
    )


def validate_conf(conf: dict)-> None:
    """
    This validates the configuration.
    """
    # App-specific part
    if isinstance(conf['app']['db_path'], click.utils.LazyFile):
        db_path = conf['app']['db_path'].name
    else:
        db_path = conf['app']['db_path']
    db_dir = os.path.dirname(os.path.realpath(db_path))
    if not os.path.exists(db_dir):
        raise FileNotFoundError("%s does not exists." % db_dir)
    if not os.access(db_dir, os.W_OK):
        raise IOError("%s not writable" % db_dir)
    res = re.match('^(\d+)\.(\d+)\.(\d+)\.(\d+)$', conf['app']['address'], re.X)
    if any(int(octet) > 255 for octet in res.groups()):
        raise ValueError("Malformed ip address: %s" % conf['app']['address'])
    if conf['app']['port'] <= 0 or conf['app']['port'] >= 2**16:
        raise ValueError("Malformed port: %s" % conf['app']['port'])
    # Mailer-specific part
    if conf['mail']:
        mailconf = conf['mail']
        if mailconf.get('address', None) is not None:
            if mailconf.get('port') is None:
                mailconf['port'] = DEFAULT_MAIL_CONF['port']
            else:
                mailconf['port'] = int(mailconf.get('port'))
            if mailconf['port'] <= 0 or mailconf['port'] >= 2**16:
                raise ValueError("Malformed mailserver port: %s" %
                                 mailconf['port'])
            if mailconf['starttls'] is None:
                mailconf['starttls'] = False
            if mailconf.get('event_timeout'):
                mailconf['event_timeout'] = parse_timeout(
                    mailconf['event_timeout']
                )
            conf['mail'] = mailconf
        else:
            conf['mail'] = dict(
                (k, None) for k in DEFAULT_MAIL_CONF.keys()
            )
    return conf


def read_conf(filepath: str = None) -> dict:
    conf = {}
    if filepath:
        conf = load_from_file(filepath)
    conf['app'] = read_section(conf, 'app', DEFAULT_APP_CONF)
    conf['mail'] = read_section(conf, 'mail', DEFAULT_MAIL_CONF)
    return validate_conf(conf)


CONF = read_conf()
