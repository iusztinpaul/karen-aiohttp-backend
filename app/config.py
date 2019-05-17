# -*- coding: utf-8 -*-
import os

import logging


def get_config(app):
    return app['config']


class Base:
    logging_level = logging.WARNING

    @classmethod
    def setup(cls, app):
        app['config'] = cls

        logging.basicConfig()
        logging.getLogger().setLevel(cls.logging_level)


class Main(Base):
    test = False
    database_url = os.environ.get('DATABASE_URL')
    logging_level = logging.INFO


class Test(Main):
    test = True
    logging_level = logging.DEBUG
