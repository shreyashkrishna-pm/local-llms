from pymongo import MongoClient
from urllib.parse import quote_plus
import certifi
from pypdf import PdfReader
import os

from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("MONGO_USER")
password = quote_plus(os.getenv("MONGO_PASSWORD"))

uri = (
    f"mongodb+srv://{username}:{password}"
    f"@firstcluster.wvt5kz6.mongodb.net/?appName=FirstCluster"
)

client = MongoClient(
    uri,
    tlsCAFile=certifi.where()
)

client.admin.command("ping")

print("✅ Connected to MongoDB")

# -----------------------------
# Database & Collection
# -----------------------------

db = client["shreyash_ai"]

documents_collection = db["documents"]

# Optional:
# Remove old documents before re-ingesting
# Comment this line out if you don't want deletion

documents_collection.delete_many({})

# -----------------------------
# PDF Extraction Function
# -----------------------------

def extract_pdf_text(filepath):

    reader = PdfReader(filepath)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

# -----------------------------
# Read PDFs From Folder
# -----------------------------

folder = "documents"

print(f"Current Directory: {os.getcwd()}")

print("Scanning PDFs...")

for filename in os.listdir(folder):

    if filename.endswith(".pdf"):

        filepath = os.path.join(folder, filename)

        print(f"Reading: {filename}")

        text = extract_pdf_text(filepath)

        document = {
            "title": filename,
            "document_type": "pdf",
            "content": text
        }

        result = documents_collection.insert_one(document)

        print(f"✅ Inserted: {filename}")
        print(f"Mongo ID: {result.inserted_id}")

# -----------------------------
# Verification
# -----------------------------

count = documents_collection.count_documents({})

print()
print(f"Total Documents in MongoDB: {count}")