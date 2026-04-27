from project_functions import (
    create_document,
    send_document,
    get_document_status,
    list_documents,
    create_contact,
    get_contact,
    list_contacts,
    update_contact,
    delete_contact,
    list_templates,
    get_template,
)

# ─────────────────────────────────────────────────────────
# REPLACE THESE before running
# ─────────────────────────────────────────────────────────
SAMPLE_TEMPLATE_ID = "VtsBQx6ppGJxLbqMoEVB6G"
SAMPLE_RECIPIENT_EMAIL = "spidyboy547@gmail.com"
SAMPLE_RECIPIENT_FIRST = "Shashidhar"
SAMPLE_RECIPIENT_LAST = "Rameshwaram"
SAMPLE_RECIPIENT_ROLE = "Employee"       # must match a role defined in the template
# ─────────────────────────────────────────────────────────


# ──────────────────────────────────────────────
# TEMPLATE TESTS
# ──────────────────────────────────────────────

def test_list_templates():
    print("\n[TEST] list_templates()")
    result = list_templates()
    templates = result.get("results", [])
    print(f"  Found {len(templates)} template(s)")
    for t in templates[:3]:
        print(f"  - {t.get('name')} | id: {t.get('id')}")
    return result


def test_get_template():
    print("\n[TEST] get_template()")
    result = get_template(SAMPLE_TEMPLATE_ID)
    print(f"  Template name : {result.get('name')}")
    print(f"  Roles         : {[r.get('name') for r in result.get('roles', [])]}")
    print(f"  Fields        : {[f.get('name') for f in result.get('fields', [])]}")
    return result


# ──────────────────────────────────────────────
# CONTACT TESTS
# ──────────────────────────────────────────────

def test_create_contact():
    print("\n[TEST] create_contact()")
    result = create_contact(
        email=SAMPLE_RECIPIENT_EMAIL,
        first_name=SAMPLE_RECIPIENT_FIRST,
        last_name=SAMPLE_RECIPIENT_LAST,
        phone="+1234567890",
        company="Acme Corp",
    )
    contact_id = result.get("id")
    print(f"  Created contact id: {contact_id}")
    return contact_id


def test_get_contact(contact_id):
    print(f"\n[TEST] get_contact({contact_id})")
    result = get_contact(contact_id)
    print(f"  Name  : {result.get('first_name')} {result.get('last_name')}")
    print(f"  Email : {result.get('email')}")
    return result


def test_list_contacts():
    print("\n[TEST] list_contacts()")
    result = list_contacts()
    contacts = result.get("results", [])
    print(f"  Found {len(contacts)} contact(s)")
    return result


def test_update_contact(contact_id):
    print(f"\n[TEST] update_contact({contact_id})")
    result = update_contact(contact_id, company="Updated Corp")
    print(f"  Updated company: {result.get('company')}")
    return result


def test_delete_contact(contact_id):
    print(f"\n[TEST] delete_contact({contact_id})")
    result = delete_contact(contact_id)
    print(f"  Deleted: {result.get('deleted')} | id: {result.get('contact_id')}")
    return result


# ──────────────────────────────────────────────
# DOCUMENT TESTS
# ──────────────────────────────────────────────

def test_create_document():
    print("\n[TEST] create_document()")
    result = create_document(
        name="Test Agreement",
        template_id=SAMPLE_TEMPLATE_ID,
        recipients=[
            {
                "email": SAMPLE_RECIPIENT_EMAIL,
                "first_name": SAMPLE_RECIPIENT_FIRST,
                "last_name": SAMPLE_RECIPIENT_LAST,
                "role": SAMPLE_RECIPIENT_ROLE,
            }
        ],
        tokens=[
            # Example: fill a token called "Client.Name" in your template
            # {"name": "Client.Name", "value": "John Doe"},
        ],
    )
    doc_id = result.get("id")
    print(f"  Created document id : {doc_id}")
    print(f"  Status              : {result.get('status')}")
    return doc_id


def test_get_document_status(document_id):
    print(f"\n[TEST] get_document_status({document_id})")
    result = get_document_status(document_id)
    print(f"  Status : {result.get('status')}")
    print(f"  Name   : {result.get('name')}")
    return result


def test_list_documents():
    print("\n[TEST] list_documents()")
    result = list_documents()
    docs = result.get("results", [])
    print(f"  Found {len(docs)} document(s)")
    for d in docs[:3]:
        print(f"  - {d.get('name')} | status: {d.get('status')}")
    return result


def test_send_document(document_id):
    """
    NOTE: Calling this will actually email the recipient.
    Only run once the document is in 'document.draft' status.
    """
    print(f"\n[TEST] send_document({document_id})")
    result = send_document(
        document_id=document_id,
        subject="Please review and sign",
        message="Hi, please review and sign the attached document. Thank you.",
    )
    print(f"  Send result: {result}")
    return result


# ──────────────────────────────────────────────
# RUNNER
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  PandaDoc API — Integration Tests")
    print("=" * 50)

    # 1. Templates
    test_list_templates()
    test_get_template()

    # 2. Contacts
    contact_id = test_create_contact()
    if contact_id:
        test_get_contact(contact_id)
        test_list_contacts()
        test_update_contact(contact_id)
        test_delete_contact(contact_id)

    # 3. Documents
    doc_id = test_create_document()
    if doc_id:
        test_get_document_status(doc_id)
        test_list_documents()

        # Uncomment ONLY when ready to send a real email to the recipient:
        # test_send_document(doc_id)

    print("\n" + "=" * 50)
    print("  All tests complete.")
    print("=" * 50)