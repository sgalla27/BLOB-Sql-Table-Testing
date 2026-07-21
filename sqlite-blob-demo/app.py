from sqlalchemy import create_engine, text

# Create SQLite database
engine = create_engine("sqlite:///files.db")

documents = [
    ("AccountForm1.pdf", "POL1001", "BIN500", "Account Form"),
    ("PolicyForm1.pdf", "POL1001", "BIN500", "Policy Form"),
    ("BinderForm1.pdf", "POL1001", "BIN500", "Binder Form"),
    ("PolicyForm2.pdf", "POL1002", "BIN501", "Policy Form"),
    ("AccountForm2.pdf", "POL1003", "BIN502", "Account Form")
]

# Create table q
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            policy_number TEXT,
            binder_number TEXT,
            document_type TEXT,
            filedata BLOB
        )
    """))
    conn.commit()


with engine.connect() as conn:
    conn.execute(text("DELETE FROM documents"))
    conn.commit()

# Load documents into database

with engine.connect() as conn:

    for filename, policy, binder, document_type in documents:

        with open(filename, "rb") as f:
            data = f.read()

        conn.execute(
            text("""
                INSERT INTO documents
                (
                    filename,
                    policy_number,
                    binder_number,
                    document_type,
                    filedata
                )
                VALUES
                (
                    :filename,
                    :policy,
                    :binder,
                    :doctype,
                    :filedata
                )
            """),
            {
                "filename": filename,
                "policy": policy,
                "binder": binder,
                "doctype": document_type,
                "filedata": data
            }
        )

    conn.commit()

print("All documents loaded.")

policy = input("Enter Policy Number: ")

with engine.connect() as conn:

    #here can filter and export certain values

    rows = conn.execute(
        text("""
            SELECT
                filename,
                document_type
            FROM documents
            WHERE policy_number = :policy
        """),
        {"policy": policy}
    ).fetchall()

print(f"\nDocuments found for {policy}:\n")

for row in rows:
    print(f"{row.filename} - {row.document_type}")



# Bulk export

import os

os.makedirs("exports", exist_ok=True)

for file in os.listdir("exports"):
    filepath = os.path.join("exports", file)

    if os.path.isfile(filepath):
        os.remove(filepath)

with engine.connect() as conn:

    rows = conn.execute(
        text("""
            SELECT
                filename,
                filedata
            FROM documents
            WHERE policy_number = :policy
        """),
        {"policy": policy}
    ).fetchall()

for row in rows:

    with open(
        f"exports/{row.filename}",
        "wb"
    ) as f:
        f.write(row.filedata)

    print(f"Exported {row.filename}")
