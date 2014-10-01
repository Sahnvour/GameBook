# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import glob
import os
import re

import yaml
from slugify import slugify_url

import dice


var_re = re.compile(r'(?!\\\\)\$([a-zA-Z]+)')


def put_vars(text, vars={}):
    return var_re.sub(lambda m: unicode(vars[m.group(1)]), text)


class StoryError(BaseException):
    pass


class PageLoadingError(StoryError):
    def __init__(self, message):
        self.message = message


class LinkError(StoryError):
    def __init__(self, message):
        self.message = message


class Link(object):
    def __init__(self, text, page=None, threshold=None, success=None,
                 failure=None):
        self.text = text
        self.page = page
        self.threshold = threshold
        self.success = success
        self.failure = failure


    def id(self, vars={}):
        if self.threshold:
            thres = put_vars(self.threshold, vars)
            return (True, self.success) if dice.roll(thres) else (
            False, self.failure)

        return (True, self.page)


    def __str__(self):
        s = "Link '" + self.text + "'"
        if self.threshold:
            s += ' with threshold \'' + self.threshold
            s += '\', success to ' + str(self.success) + ', failure to '
            s += str(self.failure)
        else:
            s += ' to ' + str(self.page)

        return s


class Page(object):
    def __init__(self, story, id, title, content, vars, links):
        self.story = story
        self.id = id
        self.title = title
        self.vars = vars
        self.links = links
        self.content = content

        self._build_links()


    def _build_links(self):
        links = []
        for l in self.links:
            if 'threshold' in l:
                links.append(
                    Link(l['text'],
                         threshold=l['threshold'],
                         success=l['success'],
                         failure=l['failure']
                    )
                )

            else:
                links.append(Link(l['text'], int(l['id'])))
        self.links = links


    def add_link(self, link):
        self.links.append(link)


    def content_with_vars(self, vars={}):
        return put_vars(self.content, vars)


    @staticmethod
    def from_stream(story, stream):
        data = yaml.load(stream)

        title = data['title']
        content = data['content']
        id = int(data['id'])
        next = []
        vars = {}

        if 'vars' in data:
            vars = {k: v for d in data['vars'] for k, v in d.items()}
        if 'next' in data:
            next = data['next']

        return Page(story, id, title, content, vars, next)


def directory(pathname):
    for f in glob.glob(pathname + '/*.yaml'):
        yield open(f, 'r')


class Story(object):
    id = 1

    def __init__(self, title, iterator=[]):
        self.id = Story.id
        Story.id += 1
        self.title = title
        self.slug = slugify_url(title)
        self.pages = {}
        for stream in iterator:
            p = Page.from_stream(self, stream)
            self.pages[p.id] = p

        for p in self.pages.itervalues():
            for l in p.links:
                if l.page:
                    if l.page not in self.pages:
                        raise LinkError(
                            self.title + ': Cannot link page %d to %d: page doesn\'t exist.' % (
                            p.id, l.page))
                else:
                    if l.success not in self.pages or l.failure not in self.pages:
                        raise LinkError(
                            self.title + ': Cannot link page %d to (%d or %d): page doesn\'t exist.' % (
                            p.id, l.success, l.failure))

        if not len(self.pages):
            raise PageLoadingError(self.title + ': No page was found.')

        if 1 not in self.pages:
            raise PageLoadingError(
                self.title + ': No page with id 1 was found.')

    def progress(self, page_id):
        return (page_id / len(self.pages)) * 100


    @staticmethod
    def from_dir(dirpath):
        title = os.path.basename(os.path.normpath(dirpath))
        return Story(title, directory(dirpath))


    def __str__(self):
        s = self.title + ':\n'
        for p in self.pages.itervalues():
            s += ' %d. %s\n' % (p.id, p.title)

        return s
