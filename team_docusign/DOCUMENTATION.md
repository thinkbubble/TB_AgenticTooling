# PandaDoc API Integration — Documentation

## Overview

This project integrates with the [PandaDoc Public API v1](https://developers.pandadoc.com/reference/about) to manage documents, contacts, and templates programmatically.

---

## Setup

### 1. Install dependencies
```bash
pip install requests python-dotenv
```

### 2. Environment variables
Create a `.env` file in the project root (never commit this file):
```
PANDADOC_API_KEY=your_api_key_here
```
Retrieve your API key from: **PandaDoc → Settings → Integrations → API**.

---

## File Structure

| File | Purpose |
|---|---|
| `project_functions.py` | All PandaDoc API calls |
| `testing.py` | Manual integration tests for each function |
| `helper.py` | Shared utilities (existing) |
| `.env` | API credentials (not committed) |

---

## Functions Reference

### Documents

#### `create_document(name, template_id, recipients, tokens=None, fields=None)`
Creates a new document from a template.

| Param | Type | Description |
|---|---|---|
| `name` | str | Display name for the document |
| `template_id` | str | UUID of the PandaDoc template |
| `recipients` | list | Each item: `{email, first_name, last_name, role}` |
| `tokens` | list | Optional. `[{name, value}]` for template token substitution |
| `fields` | dict | Optional. Pre-filled field values keyed by field name |

**Returns:** Document object including `id` and `status`

---

#### `send_document(document_id, subject, message)`
Sends a document to recipients for signing. Triggers an email notification.

| Param | Type | Description |
|---|---|---|
| `document_id` | str | ID returned from `create_document` |
| `subject` | str | Email subject line |
| `message` | str | Optional body message |

> **Note:** The document must be in `document.draft` status before sending.

---

#### `get_document_status(document_id)`
Returns current status and metadata of a document.

**Possible statuses:**
- `document.draft` — created, not yet sent
- `document.sent` — sent to recipients
- `document.viewed` — at least one recipient has opened it
- `document.completed` — all parties have signed
- `document.declined` — a recipient declined to sign

---

#### `list_documents(status=None, count=50)`
Lists documents in the workspace. Filter by status using the values above.

---

### Contacts

#### `create_contact(email, first_name, last_name, phone=None, company=None)`
Creates a new contact. Email must be unique across the workspace.

#### `get_contact(contact_id)`
Retrieves a single contact by their PandaDoc ID.

#### `list_contacts()`
Returns all contacts in the workspace.

#### `update_contact(contact_id, **kwargs)`
Updates any field on an existing contact. Pass fields as keyword arguments:
```python
update_contact("abc123", company="New Corp", phone="+19876543210")
```

#### `delete_contact(contact_id)`
Permanently deletes a contact. This cannot be undone.

---

### Templates

#### `list_templates(tag=None, count=50)`
Lists available templates. Filter by tag if your templates are tagged.

#### `get_template(template_id)`
Returns full template details including defined roles, fields, and tokens. Useful for knowing exactly what `recipients[role]`, `fields`, and `tokens` to pass when creating a document.

---

## Running Tests

Edit the constants at the top of `testing.py`:
```python
SAMPLE_TEMPLATE_ID      = "your-template-uuid"
SAMPLE_RECIPIENT_EMAIL  = "signer@yourdomain.com"
SAMPLE_RECIPIENT_FIRST  = "Jane"
SAMPLE_RECIPIENT_LAST   = "Smith"
SAMPLE_RECIPIENT_ROLE   = "Signer"   # must match a role in your template
```

Then run:
```bash
python testing.py
```

> The `test_send_document()` call is commented out by default — uncomment only when ready to send a real email to the recipient.

---

## Error Handling

All functions call `response.raise_for_status()`, which raises a `requests.HTTPError` on 4xx/5xx responses. Wrap calls in try/except for production use:

```python
import requests

try:
    doc = create_document(...)
except requests.HTTPError as e:
    print(f"API error {e.response.status_code}: {e.response.text}")
```

Common errors:
| Code | Meaning |
|---|---|
| 400 | Bad request — check payload structure |
| 401 | Invalid or missing API key |
| 404 | Document/contact/template not found |
| 429 | Rate limit exceeded |

---

## API Reference

Full PandaDoc API docs: https://developers.pandadoc.com/reference/about