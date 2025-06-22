OWNER = "Teamabeille"
REPO = "Pet-Collector-XXL"
BRANCH = "main"

API_TREE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/"
LOCAL_VERSION_FILE = "version.json"
REMOTE_VERSION_URL = RAW_BASE_URL + "version.json"
TEMP_DIR = "_repo_temp"
CURRENT_SCRIPT = os.path.basename(__file__)

def get_local_version():
    try:
        with open(LOCAL_VERSION_FILE, "r") as f:
            return json.load(f)["version"]
    except:
        return "0.0.0"

def get_remote_version():
    try:
        r = requests.get(REMOTE_VERSION_URL)
        return r.json()["version"]
    except:
        return None

def get_file_list_from_github():
    r = requests.get(API_TREE_URL)
    tree = r.json()["tree"]
    return [f["path"] for f in tree if f["type"] == "blob"]

def download_file(path, target_folder):
    url = RAW_BASE_URL + path
    local_path = os.path.join(target_folder, path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True) if "/" in path else None
    r = requests.get(url)
    if r.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(r.content)

def update_repo():
    print("📥 Téléchargement du dépôt...")
    files = get_file_list_from_github()

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    for file_path in files:
        download_file(file_path, TEMP_DIR)

    print("🧹 Nettoyage du dossier local…")
    for item in os.listdir():
        if item != CURRENT_SCRIPT and item != TEMP_DIR:
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)

    print("📂 Copie des fichiers (sauf le script actuel)…")
    for root, _, files in os.walk(TEMP_DIR):
        for file in files:
            rel_dir = os.path.relpath(root, TEMP_DIR)
            rel_file = os.path.join(rel_dir, file) if rel_dir != "." else file
            if rel_file == CURRENT_SCRIPT:
                continue
            src = os.path.join(root, file)
            dst = os.path.join(".", rel_file)
            os.makedirs(os.path.dirname(dst), exist_ok=True) if "/" in dst else None
            shutil.copy2(src, dst)

    print("📄 Téléchargement de la nouvelle version de ddd.py…")
    new_dddp = os.path.join(TEMP_DIR, CURRENT_SCRIPT)
    with open(CURRENT_SCRIPT, "wb") as f:
        f.write(open(new_dddp, "rb").read())

    shutil.rmtree(TEMP_DIR)
    print("✅ Mise à jour terminée. Redémarrage...")

    subprocess.Popen([sys.executable, CURRENT_SCRIPT])
    sys.exit()

def main():
    local = get_local_version()
    remote = get_remote_version()
    print(f"Version locale : {local} — distante : {remote}")

    if remote and local != remote:
        print("🔄 Mise à jour requise.")
        update_repo()
    else:
        print("✅ Tu es déjà à jour.")

if __name__ == "__main__":
    main()
