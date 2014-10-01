# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask import render_template, session, redirect, url_for, flash
from slugify import slugify_url

from app import app, stories
from story import put_vars


@app.context_processor
def inject():
    return dict(slugify=slugify_url, put_vars=put_vars, len=len, int=int)


@app.errorhandler(404)
def page_not_found(e):
    flash('The requested page does not exist.', 'warning')
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stories/')
def story_list():
    runs = {k: v[0] for k, v in session.iteritems()}
    return render_template('stories.html', stories=stories.values(), runs=runs)


@app.route('/story/reset/all')
@app.route('/story/reset/<story_title>')
def reset(story_title=None):
    if story_title:
        session.pop(story_title)
        flash(
            'Your story \'' + stories[story_title].title + '\' has been reset.',
            'info')
    else:
        for story in stories.itervalues():
            if story.slug in session:
                session.pop(story.slug)
        flash('All stories have been reset.', 'info')

    return redirect(url_for('story_list'))


@app.route('/story/<story_title>/')
@app.route('/story/<story_title>/<int:page_id>')
def story_view(story_title, page_id=None):
    # Invalid story
    if story_title not in stories:
        flash('Story doesn\'t exist.', 'danger')
        return redirect(url_for('story_list'))

    run = None
    if story_title in session:
        # run = (current_page, vars)
        run = session[story_title]

    # Already doing this story but no page specified
    if not page_id and run:
        page_id = run[0]

        return redirect(url_for('story_view',
                                story_title=story_title, page_id=page_id))

    story = stories[story_title]

    # Beginning a story
    if not run:
        page = story.pages[1]
        run = (1, page.vars)
        session[story_title] = run

        return redirect(
            url_for('story_view', story_title=story_title, page_id=1))

    if page_id and run:
        # Incorrect page_id
        if page_id != run[0]:
            correct_id = run[0]

            return redirect(url_for('story_view',
                                    story_title=story_title,
                                    page_id=correct_id))
        # Display correct page
        else:
            page = story.pages[run[0]]

            return render_template('page.html', story=story, page=page,
                                   vars=run[1], story_title=story_title)


@app.route('/story/<story_title>/<int:page_id>/go/<int:link_id>')
def follow_link(story_title, page_id, link_id):
    if story_title not in stories:
        return redirect(url_for('story_list'))

    run = None
    if story_title in session:
        run = session[story_title]

    if not run:
        return redirect(url_for('story_view', story_title=story_title))

    if run[0] != page_id:
        return redirect(url_for('story_view', story_title=story_title))

    story = stories[story_title]
    page = story.pages[run[0]]
    vars = run[1]

    link = page.links[link_id]
    success, id = link.id(vars)
    if not link.page:
        if success:
            flash('Success!', 'success')
        else:
            flash('Epic fail ...', 'warning')

    for k, v in story.pages[id].vars.iteritems():
        vars[k] = v
    session[story_title] = (id, vars)

    return redirect(url_for('story_view', story_title=story_title, page_id=id))
