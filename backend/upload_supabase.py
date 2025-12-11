import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET = "uploads"

files_to_upload = [
    ("upload_leis.csv", "upload_leis.csv"),
    ("upload_eventos.csv", "upload_eventos.csv"),
    ("upload_votos.csv", "upload_votos.csv"),
]

def upload_file(local_file, remote_name):
    if not os.path.exists(local_file):
        print(f"Arquivo não encontrado localmente: {local_file}")
        return

    try:
        supabase.storage.from_(BUCKET).remove([remote_name])
    except Exception:
        pass

    print(f"Enviando {local_file}...")
    with open(local_file, "rb") as f:
        result = supabase.storage.from_(BUCKET).upload(remote_name, f)
    print(f" OK: {remote_name}")

for local, remote in files_to_upload:
    upload_file(local, remote)

print("\nUpload finalizado!")
