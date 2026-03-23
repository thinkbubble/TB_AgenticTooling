# Agentic Tooling Team


## 1. Setup

1. Clone the repo and enter the folder:
   ```bash
   git clone git@github.com:thinkbubble/TB_your_first_name.git
   cd TB_your_first_name
   ```
2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```


---


## 2. File Overview

| File | Purpose |
|------|---------|
| `.gitignore` | Never touch this. |
| `.env` | API keys and secrets — never commit (handled by .gitignore) |
| `helper.py` | Shared, platform-agnostic utility functions. DO NOT make changes to these functions. |
| `new_helper.py` | Candidate functions for promotion to `helper.py` Review coding_guidelines.pdf on Sharepoint for in-depth instructions and expectations. |
| `app.py` | Webhook endpoint (Flask) |
| `DOCUMENTATION.md` | This file is where you will put all your documentation as you progress. You must delete or change items that become irrelevant or are no longer used. This document must be kept current, non-verbose and clean. Review documentation_guidelines.pdf on Sharepoint for in-depth instructions and expectations. |
| `requirements.txt` | Pinned dependencies |
| `project_report.pdf` | Project report. This goes in your platform specific folder. |
| `project_functions.py` | Platform-specific functions and logic OR dataset, cleaning, scaling, training and interpreting results logic. Review coding_guidelines.pdf on Sharepoint for in-depth instructions and expectations. |
| `testing.py` | Tests for `project_functions.py` Review coding_guidelines.pdf on Sharepoint for in-depth instructions and expectations.|

---

## 3. .env

- Add all required API keys here
- Never commit this file (already in `.gitignore`)
- Format:
  ```
  MY_API_KEY=your_key_here
  ```

---

## 4. ngrok Setup

1. Create an account at [ngrok.com](https://ngrok.com)
2. Install ngrok: **Getting Started → Setup & Installation** (choose your OS)
3. Get your domain: **Universal Gateway → Domains**
4. Bind to Flask port:
   ```bash
   ngrok http --domain=your_domain_here 5000
   ```
   - Works on macOS/Linux; ask an LLM to convert for Windows if needed
5. Start your Flask app in a separate terminal — ngrok will forward webhook traffic to it

---

## 5. project_functions.py

> Document each function as you build them. 

### `function_name(param1, param2)`
- **What it does:** One sentence.
- **Params:** `param1` — description. `param2` — description.
- **Returns:** What it returns.

---

## 6. testing.py
> This is where you will write test functions for all of your project_functions and/or training pipelines.

> Document how you're using your platform functions.

### Test: `test_name`
- **Tests:** Which function(s)
- **How:** Brief description of what you're testing and how
- **Expected:** What a passing result looks like

---

## 7. Working on Your Branch

1. Before starting work each day, pull the latest `main` branch:
   ```bash
   git checkout main
   git pull origin main
   ```

2. Create or switch to your personal feature branch:
   ```bash
   git checkout -b yourname_feature
   ```
   If your branch already exists:
   ```bash
   git checkout yourname_feature
   ```

3. Do your work on your branch only. Never work directly on `main`.

4. Keep installs clean. If you pip install something and don't use it:
   ```bash
   pip uninstall package_name
   ```

5. Freeze requirements before pushing if dependencies changed:
   ```bash
   pip freeze > requirements.txt
   ```

6. Commit and push your branch:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   git push origin yourname_feature
   ```

7. You should push your branch at the end of each day you work. This ensures your latest work is visible for review.

8. After pushing your branch, if you have done a sizable amount of work, you must create a Pull Request (PR) for review.

### Creating a Pull Request (GitHub UI)

1. Go to the repository on GitHub in your browser.

2. You will see a banner that says your branch was recently pushed.

3. Click:
   ```text
   Compare & pull request
   ```

4. Confirm the following:
   ```text
   base: main
   compare: yourname_feature
   ```

5. Add:
   - A clear title describing your changes
   - A short description of what you implemented

6. Click:
   ```text
   Create pull request
   ```

7. Your code will now be reviewed before being merged into `main`.

---

### Important

- Pushing your branch makes your work visible.
- Creating a Pull Request is required for review and merging into `main`.
- All work must go through a Pull Request before being added to `main`.

## 8. Pulling from GitHub

1. Always pull the latest changes before you begin working to ensure your local environment is up to date with any reviewed or updated code.:
   ```bash
   git pull origin main
   ```

2. If Git says there is a conflict, stop and resolve it before continuing. If you are unsure how to resolve a conflict, stop and ask before guessing.

3. Open the file(s) Git lists as conflicted. incoming code is the changes I made to your project and are prioritized over your code. your code may need to be adapted to work with incoming code.

4. Look for conflict markers that look like this:
   ```text
   <<<<<<< HEAD
   your code
   =======
   incoming code
   >>>>>>> branch-name
   ```

5. Edit the file so that it contains the correct final code. Delete the conflict markers when you are done.

6. Save the file.

7. Stage the resolved file(s):
   ```bash
   git add .
   ```

8. Complete the merge:
   ```bash
   git commit
   ```

9. Push your updated code:
   ```bash
   git push origin main
   ```

## 9. Syncing Your Branch with Main

1. Before continuing work on an older branch, first update `main`:
   ```bash
   git checkout main
   git pull origin main
   ```

2. Then switch back to your branch:
   ```bash
   git checkout yourname_feature
   ```

3. Merge the latest `main` into your branch:
   ```bash
   git merge main
   ```

4. If Git says there is a conflict, stop and resolve it before continuing. If you are unsure how to resolve a conflict, stop and ask before guessing.

5. Open the file(s) Git lists as conflicted. Incoming code is the reviewed or updated code from `main` and is prioritized over old code unless there is a clear reason to preserve your version.

6. Look for conflict markers that look like this:
   ```text
   <<<<<<< HEAD
   your code
   =======
   incoming code
   >>>>>>> main
   ```

7. Edit the file so that it contains the correct final code. Delete the conflict markers when you are done.

8. Save the file, then stage the resolved file(s):
   ```bash
   git add .
   ```

9. Complete the merge:
   ```bash
   git commit
   ```

10. Push your updated branch:
   ```bash
   git push origin yourname_feature
   ```


## 10. Webhooks

1. These must be setup in the platform itself and will forward to your ngrok. Your webhooks will not work until this is done. ie. you will not receive any data from the platform until this is setup.