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
| `project_report.pdf` | Project report |
| `project_functions.py` | Platform-specific functions and logic OR dataset, cleaning, scaling, training and interpreting results logic. Review coding_guidelines.pdf on Sharepoint for in-depth instructions and expectations. |
| `testing.py` | Tests for `project_functions.py` Review coding_guidelines.pdf on Sharepoint for in-depth instructions and expectations.|
| `ingestion.py` | ONLY FOR MDQML. Functions to ingest your data. May or may not need to be made more robust for your dataset. If you make any changes to these functions, you must put it into EDITS.md. |

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

## 7. Pushing to GitHub

1. Keep installs clean — if you pip install something and don't use it:
   ```bash
   pip uninstall package_name
   ```
2. Freeze requirements before pushing:
   ```bash
   pip freeze > requirements.txt
   ```
3. Commit and push:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   git push origin main
   ```
4. You should be pushing at the end of each day you work. This ensures that whenever Jon or I do a code review, we are seeing your most up to date work. This is critical, because as we move forward, I will be absorbing your contributions into larger projects.

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

## 9. Webhooks

1. These must be setup in the platform itself and will forward to your ngrok. Your webhooks will not work until this is done. ie. you will not receive any data from the platform until this is setup.