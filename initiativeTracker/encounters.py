# INF601 - Advanced Programming in Python
# Gage Giffin
# Mini Project 5

import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from initiativeTracker.auth import login_required
from initiativeTracker.db import get_db

bp = Blueprint('encounters', __name__, url_prefix='/encounters')

COMBATANT_TYPES = ('PC', 'Monster', 'NPC')


@bp.route('/')
@login_required
def index():
    db = get_db()
    encounters = db.execute(
        'SELECT e.id, e.name, e.description, e.created, COUNT(c.id) AS combatant_count'
        ' FROM encounter e LEFT JOIN combatant c ON c.encounter_id = e.id'
        ' WHERE e.user_id = ?'
        ' GROUP BY e.id'
        ' ORDER BY e.created DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('encounters/index.html', encounters=encounters)


def get_encounter(id):
    encounter = get_db().execute(
        'SELECT * FROM encounter WHERE id = ?', (id,)
    ).fetchone()

    if encounter is None:
        abort(404, f"Encounter id {id} doesn't exist.")

    if encounter['user_id'] != g.user['id']:
        abort(403)

    return encounter


def get_combatant(encounter_id, id):
    combatant = get_db().execute(
        'SELECT * FROM combatant WHERE id = ? AND encounter_id = ?',
        (id, encounter_id)
    ).fetchone()

    if combatant is None:
        abort(404, f"Combatant id {id} doesn't exist.")

    return combatant


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()

        if not name:
            flash('Name is required.')
        else:
            db = get_db()
            cursor = db.execute(
                'INSERT INTO encounter (user_id, name, description) VALUES (?, ?, ?)',
                (g.user['id'], name, description)
            )
            db.commit()
            return redirect(url_for('encounters.detail', id=cursor.lastrowid))

    return render_template('encounters/create.html')


@bp.route('/<int:id>')
@login_required
def detail(id):
    encounter = get_encounter(id)
    combatants = get_db().execute(
        'SELECT * FROM combatant WHERE encounter_id = ?'
        ' ORDER BY initiative DESC, name',
        (id,)
    ).fetchall()
    return render_template(
        'encounters/detail.html',
        encounter=encounter,
        combatants=combatants,
        combatant_types=COMBATANT_TYPES,
    )


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    encounter = get_encounter(id)

    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()

        if not name:
            flash('Name is required.')
        else:
            db = get_db()
            db.execute(
                'UPDATE encounter SET name = ?, description = ? WHERE id = ?',
                (name, description, id)
            )
            db.commit()
            return redirect(url_for('encounters.detail', id=id))

    return render_template('encounters/update.html', encounter=encounter)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_encounter(id)
    db = get_db()
    db.execute('DELETE FROM encounter WHERE id = ?', (id,))
    db.commit()
    flash('Encounter deleted.')
    return redirect(url_for('encounters.index'))


def read_combatant_form(form):
    """Validate the add/edit combatant form. Returns (values, error)."""
    values = {
        'name': form['name'].strip(),
        'type': form['type'],
    }

    try:
        # initiative is optional since it can be rolled later
        values['initiative'] = int(form['initiative'] or 0)
        values['initiative_modifier'] = int(form['initiative_modifier'] or 0)
        values['max_hp'] = int(form['max_hp'])
        values['armor_class'] = int(form['armor_class']) if form['armor_class'] else None
    except ValueError:
        return values, 'Initiative, modifier, HP, and AC must be whole numbers.'

    if not values['name']:
        return values, 'Name is required.'
    if values['type'] not in COMBATANT_TYPES:
        return values, 'Invalid combatant type.'
    if values['max_hp'] < 1:
        return values, 'Max HP must be at least 1.'

    return values, None


@bp.route('/<int:id>/combatants/add', methods=('POST',))
@login_required
def add_combatant(id):
    get_encounter(id)
    values, error = read_combatant_form(request.form)

    if error is None:
        db = get_db()
        db.execute(
            'INSERT INTO combatant'
            ' (encounter_id, name, type, initiative, initiative_modifier, max_hp, current_hp, armor_class)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (id, values['name'], values['type'], values['initiative'], values['initiative_modifier'],
             values['max_hp'], values['max_hp'], values['armor_class'])
        )
        db.commit()
    else:
        flash(error)

    return redirect(url_for('encounters.detail', id=id))


@bp.route('/<int:id>/combatants/<int:cid>/update', methods=('POST',))
@login_required
def update_combatant(id, cid):
    get_encounter(id)
    get_combatant(id, cid)
    values, error = read_combatant_form(request.form)

    if error is None:
        try:
            current_hp = int(request.form['current_hp'])
        except ValueError:
            error = 'Current HP must be a whole number.'
        else:
            # keep current HP between 0 and the (possibly new) max HP
            current_hp = max(0, min(current_hp, values['max_hp']))

    if error is None:
        db = get_db()
        db.execute(
            'UPDATE combatant SET name = ?, type = ?, initiative = ?, initiative_modifier = ?,'
            ' max_hp = ?, current_hp = ?, armor_class = ?'
            ' WHERE id = ?',
            (values['name'], values['type'], values['initiative'], values['initiative_modifier'],
             values['max_hp'], current_hp, values['armor_class'], cid)
        )
        db.commit()
    else:
        flash(error)

    return redirect(url_for('encounters.detail', id=id))


@bp.route('/<int:id>/roll', methods=('POST',))
@login_required
def roll_initiative(id):
    get_encounter(id)
    db = get_db()
    combatants = db.execute(
        'SELECT id, initiative_modifier FROM combatant WHERE encounter_id = ?', (id,)
    ).fetchall()

    for c in combatants:
        roll = random.randint(1, 20) + c['initiative_modifier']
        db.execute('UPDATE combatant SET initiative = ? WHERE id = ?', (roll, c['id']))
    db.commit()

    flash('Rolled initiative for all combatants.')
    return redirect(url_for('encounters.detail', id=id))


@bp.route('/<int:id>/combatants/<int:cid>/hp', methods=('POST',))
@login_required
def adjust_hp(id, cid):
    get_encounter(id)
    combatant = get_combatant(id, cid)

    try:
        amount = int(request.form['amount'])
    except ValueError:
        amount = -1

    if amount < 0:
        flash('HP amount must be a positive whole number.')
        return redirect(url_for('encounters.detail', id=id))

    if request.form['action'] == 'heal':
        new_hp = min(combatant['current_hp'] + amount, combatant['max_hp'])
    else:
        new_hp = max(combatant['current_hp'] - amount, 0)

    db = get_db()
    db.execute('UPDATE combatant SET current_hp = ? WHERE id = ?', (new_hp, cid))
    db.commit()
    return redirect(url_for('encounters.detail', id=id))


@bp.route('/<int:id>/combatants/<int:cid>/delete', methods=('POST',))
@login_required
def delete_combatant(id, cid):
    get_encounter(id)
    get_combatant(id, cid)
    db = get_db()
    db.execute('DELETE FROM combatant WHERE id = ?', (cid,))
    db.commit()
    return redirect(url_for('encounters.detail', id=id))
