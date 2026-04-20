from dotenv import load_dotenv
from helper import *
import os
import requests

load_dotenv()

PANDADOC_API_KEY = os.getenv("PANDADOC_API_KEY")
BASE_URL = "https://api.pandadoc.com/public/v1"


def _get_headers():
    """Return auth headers for every PandaDoc request."""
    return {
        "Authorization": f"API-Key {PANDADOC_API_KEY}",
        "Content-Type": "application/json",
    }


# ──────────────────────────────────────────────
# DOCUMENTS
# ──────────────────────────────────────────────

def create_document(name, template_id, recipients, tokens=None, fields=None):
    """
    Create a new document from a template.

    Args:
        name         (str):  Display name for the document.
        template_id  (str):  UUID of the PandaDoc template to use.
        recipients   (list): List of dicts, each with keys:
                             email, first_name, last_name, role
        tokens       (list): Optional. List of {name, value} dicts for
                             template token substitution.
        fields       (dict): Optional. Field values keyed by field name.

    Returns:
        dict: Created document object (includes 'id' and 'status').
    """
    payload = {
        "name": name,
        "template_uuid": template_id,
        "recipients": recipients,
    }
    if tokens:
        payload["tokens"] = tokens
    if fields:
        payload["fields"] = fields

    response = requests.post(
        f"{BASE_URL}/documents",
        headers=_get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def send_document(document_id, subject="Please sign this document", message=""):
    """
    Send a document to its recipients for signing.

    Args:
        document_id (str): ID of the document to send.
        subject     (str): Email subject line sent to signers.
        message     (str): Optional body message sent to signers.

    Returns:
        dict: API response confirming the send action.
    """
    payload = {
        "subject": subject,
        "message": message,
        "silent": False,
    }
    response = requests.post(
        f"{BASE_URL}/documents/{document_id}/send",
        headers=_get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def get_document_status(document_id):
    """
    Retrieve the current status and details of a document.

    Args:
        document_id (str): ID of the document.

    Returns:
        dict: Document object including 'status' field.
              Possible statuses: document.draft, document.sent,
              document.viewed, document.completed, document.declined.
    """
    response = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        headers=_get_headers(),
    )
    response.raise_for_status()
    return response.json()


def list_documents(status=None, count=50):
    """
    List documents in your PandaDoc workspace.

    Args:
        status (str):  Optional status filter (e.g. 'document.sent').
        count  (int):  Max number of results to return (default 50).

    Returns:
        dict: Paginated list of document objects.
    """
    params = {"count": count}
    if status:
        params["status"] = status

    response = requests.get(
        f"{BASE_URL}/documents",
        headers=_get_headers(),
        params=params,
    )
    response.raise_for_status()
    return response.json()


# ──────────────────────────────────────────────
# CONTACTS
# ──────────────────────────────────────────────

def create_contact(email, first_name, last_name, phone=None, company=None):
    """
    Create a new contact in PandaDoc.

    Args:
        email      (str): Contact's email address (required, must be unique).
        first_name (str): Contact's first name.
        last_name  (str): Contact's last name.
        phone      (str): Optional phone number.
        company    (str): Optional company name.

    Returns:
        dict: Created contact object (includes 'id').
    """
    payload = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
    }
    if phone:
        payload["phone"] = phone
    if company:
        payload["company"] = company

    response = requests.post(
        f"{BASE_URL}/contacts",
        headers=_get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def get_contact(contact_id):
    """
    Retrieve a single contact by ID.

    Args:
        contact_id (str): The contact's PandaDoc ID.

    Returns:
        dict: Contact object.
    """
    response = requests.get(
        f"{BASE_URL}/contacts/{contact_id}",
        headers=_get_headers(),
    )
    response.raise_for_status()
    return response.json()


def list_contacts():
    """
    List all contacts in your PandaDoc workspace.

    Returns:
        dict: List of contact objects.
    """
    response = requests.get(
        f"{BASE_URL}/contacts",
        headers=_get_headers(),
    )
    response.raise_for_status()
    return response.json()


def update_contact(contact_id, **kwargs):
    """
    Update fields on an existing contact.

    Args:
        contact_id (str): The contact's PandaDoc ID.
        **kwargs:         Any updatable fields (email, first_name,
                          last_name, phone, company, etc.).

    Returns:
        dict: Updated contact object.
    """
    response = requests.patch(
        f"{BASE_URL}/contacts/{contact_id}",
        headers=_get_headers(),
        json=kwargs,
    )
    response.raise_for_status()
    return response.json()


def delete_contact(contact_id):
    """
    Delete a contact from PandaDoc.

    Args:
        contact_id (str): The contact's PandaDoc ID.

    Returns:
        dict: Confirmation with the deleted contact_id.
    """
    response = requests.delete(
        f"{BASE_URL}/contacts/{contact_id}",
        headers=_get_headers(),
    )
    response.raise_for_status()
    return {"deleted": True, "contact_id": contact_id}


# ──────────────────────────────────────────────
# TEMPLATES
# ──────────────────────────────────────────────

def list_templates(tag=None, count=50):
    """
    List available templates in your PandaDoc workspace.

    Args:
        tag   (str): Optional tag to filter templates.
        count (int): Max number of results to return (default 50).

    Returns:
        dict: List of template objects (each includes 'id' and 'name').
    """
    params = {"count": count}
    if tag:
        params["tag"] = tag

    response = requests.get(
        f"{BASE_URL}/templates",
        headers=_get_headers(),
        params=params,
    )
    response.raise_for_status()
    return response.json()


def get_template(template_id):
    """
    Get full details of a specific template, including its fields and roles.

    Args:
        template_id (str): The template's UUID.

    Returns:
        dict: Full template detail object (fields, roles, tokens, etc.).
    """
    response = requests.get(
        f"{BASE_URL}/templates/{template_id}/details",
        headers=_get_headers(),
    )
    response.raise_for_status()
    return response.json()