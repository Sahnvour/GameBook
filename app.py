# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os

from flask import Flask
from story import Story, StoryError


app = None

stories = {}


def _load_stories():
    for subdir, dirs, files in os.walk('stories/'):
        for dir in dirs:
            try:
                s = Story.from_dir('stories/' + dir)
                stories[s.slug] = s
            except StoryError as e:
                print e.message


def create_app():
    global app
    app = Flask(__name__)
    app.config.from_object('config')

    import views
    # DebugToolbarExtension(app)
    _load_stories()

    return app
