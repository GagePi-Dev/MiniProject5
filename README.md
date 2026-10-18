# Initiative Tracker

A Flask web app for Dungeon Masters to run combat in Dungeons & Dragons and other tabletop games.
Users register and log in, build encounters, add players and monsters, roll initiative for everyone
at once, and track hit points as the fight goes on.

Built for INF601 - Advanced Programming in Python, Mini Project 5.

## Features

- **Accounts:** Register and log in; each user only sees their own encounters.
- **Encounters:** Create, edit, and delete encounters with a name and description.
- **Combatants:** Add PCs, Monsters, and NPCs with initiative, initiative modifier, HP, and AC, then edit or remove them.
- **Roll Initiative:** One button rolls a d20 plus each combatant's modifier and re-sorts the turn order.
- **HP tracking:** Inline **−** / **+** controls on every row apply damage or healing. HP bars change color as health drops, and combatants at 0 HP are marked "Down."
- **Bootstrap modals:** Add Combatant, Edit Combatant, and a delete confirmation for encounters.

## Tech Stack

- Python 3 and [Flask](https://flask.palletsprojects.com/) 3.1
- SQLite (built into Python)
- [Bootstrap](https://getbootstrap.com/) 5.3.3 loaded from the jsDelivr CDN

## Project Structure

The layout follows the official [Flask tutorial](https://flask.palletsprojects.com/en/stable/tutorial/).

```
├── initiativeTracker/
│   ├── __init__.py          # application factory (create_app)
│   ├── db.py                # database connection and init-db command
│   ├── schema.sql           # table definitions
│   ├── main.py              # Home and About pages
│   ├── auth.py              # register, login, logout
│   ├── encounters.py        # encounters, combatants, initiative, HP
│   ├── static/
│   └── templates/
│       ├── base.html        # shared layout every page extends
│       ├── home.html
│       ├── about.html
│       ├── auth/
│       │   ├── register.html
│       │   └── login.html
│       └── encounters/
│           ├── index.html   # My Encounters
│           ├── create.html  # New Encounter form
│           ├── update.html  # Edit Encounter form + delete modal
│           └── detail.html  # the tracker + Add/Edit Combatant modals
├── requirements.txt
└── README.md
```

## Database

SQLite with three tables linked by foreign keys:

```
user ──< encounter ──< combatant
     user_id      encounter_id
```

| Table | Columns |
|---|---|
| `user` | `id`, `username`, `password` (hashed) |
| `encounter` | `id`, `user_id` → `user.id`, `created`, `name`, `description` |
| `combatant` | `id`, `encounter_id` → `encounter.id`, `name`, `type`, `initiative`, `initiative_modifier`, `max_hp`, `current_hp`, `armor_class` |

Both foreign keys use `ON DELETE CASCADE`, so deleting an encounter also deletes its combatants.

## Setup

These steps assume Python 3 is installed. Run all commands from the project's root folder.

**1. Clone the repository**

```bash
git clone https://github.com/GagePi-Dev/MiniProject5.git
cd MiniProject5
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
```

- macOS / Linux: `source .venv/bin/activate`
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`

**3. Install the requirements**

```bash
pip install -r requirements.txt
```

**4. Create a secret key**

Flask uses a secret key to sign login cookies. Generate a random one and save it to `instance/config.py`
(the `instance/` folder is git-ignored, so the key is never committed):

```bash
python -c "import secrets, pathlib; p = pathlib.Path('instance'); p.mkdir(exist_ok=True); (p / 'config.py').write_text('SECRET_KEY = ' + repr(secrets.token_hex(32)) + chr(10))"
```

If you skip this step the app still runs, but it generates a new random key every time it starts,
so everyone is logged out whenever the server restarts.

**5. Initialize the database**

```bash
flask --app initiativeTracker init-db
```

This creates `instance/initiativeTracker.sqlite`. Running it again **deletes all data** and starts fresh.

## Running the Development Server

```bash
flask --app initiativeTracker run --debug
```

Then open <http://127.0.0.1:5000/> in your browser, register an account, and create your first encounter.
`--debug` reloads the server automatically when code changes.

## Security

- Passwords are hashed with Werkzeug and never stored in plain text.
- The secret key comes from `instance/config.py` (or a random fallback) instead of being hardcoded.
- Session cookies use `SameSite=Lax`, so other websites can't submit forms using your login.
- Login shows one "Incorrect username or password" message, so it doesn't reveal which usernames exist.
- Logout, deletes, and all other changes are POST-only.
- Every encounter and combatant route checks that the logged-in user owns it.
- All SQL uses parameterized queries, and Jinja escapes all output.
- Input lengths and number ranges are checked on the server, with matching limits in the forms.
- Bootstrap is loaded with Subresource Integrity hashes.

## Limitations

- **Development server only.** The Flask dev server and `--debug` mode are not meant for production, and there's no HTTPS.
- **No login rate limiting.** Unlimited password attempts are allowed (this would need a package like Flask-Limiter).
- **No CSRF tokens.** Cross-site form protection relies on `SameSite=Lax` cookies rather than per-form tokens (like Flask-WTF).
- **No turn tracking.** The tracker shows initiative order but doesn't track whose turn it is or count rounds.
- **Roll Initiative re-rolls everyone,** including PCs whose players may have rolled their own dice. Ties are sorted by name.
- **No account management.** There is no password reset, password change, or account deletion.
- **Removing a combatant has no confirmation** (deleting an encounter does).
- **Encounters are private.** They can't be shared with other users or players.

## AI Usage

**Model used:** Claude Opus 5.5 (Anthropic), via Claude Code

- Brainstormed project ideas and helped scope the Initiative Tracker concept, including a suggested database layout and page list.
- Created this README file and the AI Usage section structure.
- Developed the baseline project structure (the `initiativeTracker` package with `templates/` and `static/` folders) based on the Flask tutorial layout, and added the required header to `__init__.py`.
- Built the Flask app based on the Flask tutorial: the app factory, database and schema, the main, auth, and encounters blueprints, and all templates with Bootstrap modals. Also added the features I requested later (combatant editing, inline HP controls, initiative modifiers, and Roll Initiative) and tested each step.
- Performed a security review and implemented the fixes I approved: a random secret key, `SameSite` cookies, a single login error message, POST-only logout, Bootstrap integrity hashes, and input length and range limits. Also wrote the full README, including setup instructions and limitations.

### What I Wrote Myself

- 

### What I Changed In AI Code

- 
