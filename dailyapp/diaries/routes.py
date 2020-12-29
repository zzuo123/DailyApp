from logging import log
from flask import Blueprint, flash, url_for, redirect, abort, request
from flask.templating import render_template
from flask_login import current_user, login_required
from dailyapp import db
from dailyapp.diaries.forms import DiaryForm
from dailyapp.models import Diary

diaries = Blueprint('diaries', __name__)


@diaries.route('/diary')
@login_required
def diary_main():
    entries = Diary.query.all()
    return render_template('diary_main.html', diaries=entries)


@diaries.route('/diary/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = DiaryForm()
    if form.validate_on_submit():
        # we call the user 'author' here because user_id in the Diary model has User backref as 'author'
        diary = Diary(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(diary)
        db.session.commit()
        flash('Your diary entry has been added!', 'success')
        return redirect(url_for('diaries.diary_main'))
    return render_template('create_entry.html', title='New Entry', legend='New Entry', form=form)


@diaries.route('/diary/<int:diary_id>')
@login_required
def diary(diary_id):
    entry = Diary.query.get_or_404(diary_id)  # get diary id or 404 if entry doesn't exist
    return render_template('diary.html', diary=entry, title=entry.title)


@diaries.route('/diary/<int:diary_id>/update', methods=['GET', 'POST'])
@login_required
def update_entry(diary_id):
    entry = Diary.query.get_or_404(diary_id)  # get diary id or 404 if entry doesn't exist
    if entry.author != current_user:
        abort(403)  # manually abort and return a http response for forbidden route
    form = DiaryForm()
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.content = form.content.data
        # when updating database, no need to have db.session.add(entry)
        db.session.commit()
        flash('Your diary entry has been updated!', 'success')
        return redirect(url_for('diaries.diary_main'))
    elif request.method == 'GET':
        form.title.data = entry.title
        form.content.data = entry.content
    return render_template('create_entry.html', title='Update Diary', legend="Update Diary", form=form)


@diaries.route('/diary/<int:diary_id>/delete', methods=['POST'])
@login_required
def delete_entry(diary_id):
    entry = Diary.query.get_or_404(diary_id)
    if entry.author != current_user:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    flash('Your diary entry has been deleted!', 'success')
    return redirect(url_for('diaries.diary_main'))