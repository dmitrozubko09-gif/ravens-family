"""
rāvenS — Discord API Backend
Запускається на Railway/Render, віддає список учасників сервера
"""

import os
import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

# ── Конфіг ──────────────────────────────────────────────
BOT_TOKEN   = os.environ.get("DISCORD_BOT_TOKEN", "")
GUILD_ID    = os.environ.get("DISCORD_GUILD_ID", "")
PORT        = int(os.environ.get("PORT", 8000))
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

# Маппінг ролей Discord → ранги на сайті
RANK_MAP = {
    "Голова сім'ї":    {"rank": "boss",      "label": "Голова сім'ї"},
    "Заступник голови":{"rank": "underboss", "label": "Заступник голови"},
    "Head Cpt":        {"rank": "capo",      "label": "Head Cpt"},
    "Dep.Head cpt":    {"rank": "capo",      "label": "Dep.Head Cpt"},
    "Старший склад":   {"rank": "soldier",   "label": "Старший склад"},
    "cpt player":      {"rank": "soldier",   "label": "Cpt Player"},
    "Член сім'ї":      {"rank": "member",    "label": "Член сім'ї"},
    "Новобранець":     {"rank": "associate", "label": "Новобранець"},
    "Рекрутер":        {"rank": "special",   "label": "Рекрутер"},
    "Куратор новачків":{"rank": "special",   "label": "Куратор новачків"},
}

# Ролі які НЕ показувати (боти, сервісні)
SKIP_ROLES = {"Бот", "carl-bot", "Server Booster", "RAVEN",
              "догана [3/3]", "догана [2/3]", "догана [1/3]"}

RANK_ORDER = ["boss", "underboss", "capo", "soldier", "member", "special", "associate"]
# ────────────────────────────────────────────────────────


def discord_request(endpoint):
    """GET запит до Discord API"""
    url = f"https://discord.com/api/v10{endpoint}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "RavensBot/1.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Discord API error {e.code}: {e.read().decode()}")
        return None


def get_members():
    """Отримати список учасників з Discord"""
    # Отримуємо ролі сервера
    roles_data = discord_request(f"/guilds/{GUILD_ID}/roles")
    if not roles_data:
        return []

    role_id_map = {r["id"]: r["name"] for r in roles_data}

    # Отримуємо учасників (до 1000)
    members_data = discord_request(f"/guilds/{GUILD_ID}/members?limit=1000")
    if not members_data:
        return []

    result = []
    for m in members_data:
        user = m.get("user", {})

        # Пропускаємо ботів
        if user.get("bot"):
            continue

        # Знаходимо найвищий ранг
        member_rank = None
        member_roles = [role_id_map.get(rid, "") for rid in m.get("roles", [])]

        for role_name in member_roles:
            if role_name in SKIP_ROLES:
                continue
            if role_name in RANK_MAP:
                info = RANK_MAP[role_name]
                if member_rank is None:
                    member_rank = info
                else:
                    # Беремо вищий ранг
                    if RANK_ORDER.index(info["rank"]) < RANK_ORDER.index(member_rank["rank"]):
                        member_rank = info

        # Якщо немає знайомого рангу — пропускаємо (боти, сервісні акаунти)
        if not member_rank:
            continue

        # Аватарка
        avatar_hash = user.get("avatar") or m.get("avatar")
        if avatar_hash:
            if m.get("avatar"):  # guild avatar пріоритет
                avatar_url = f"https://cdn.discordapp.com/guilds/{GUILD_ID}/users/{user['id']}/avatars/{m['avatar']}.png?size=64"
            else:
                avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{avatar_hash}.png?size=64"
        else:
            avatar_url = None

        # Нікнейм
        display_name = m.get("nick") or user.get("global_name") or user.get("username", "Unknown")

        result.append({
            "id":          user.get("id"),
            "name":        display_name,
            "username":    user.get("username"),
            "avatar":      avatar_url,
            "rank":        member_rank["rank"],
            "rankLabel":   member_rank["label"],
            "roles":       [r for r in member_roles if r and r not in SKIP_ROLES],
        })

    # Сортуємо за рангом
    result.sort(key=lambda x: RANK_ORDER.index(x["rank"]) if x["rank"] in RANK_ORDER else 99)
    return result


def get_online_status():
    """Отримати онлайн статуси через Guild Presences"""
    # Потребує GUILD_PRESENCES intent — повертаємо базову інфу
    data = discord_request(f"/guilds/{GUILD_ID}?with_counts=true")
    if data:
        return {
            "online":       data.get("approximate_presence_count", 0),
            "total":        data.get("approximate_member_count", 0),
        }
    return {"online": 0, "total": 0}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/api/members":
            members = get_members()
            counts  = get_online_status()
            payload = json.dumps({
                "members": members,
                "online":  counts["online"],
                "total":   counts["total"],
            }, ensure_ascii=False)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors()
            self.end_headers()
            self.wfile.write(payload.encode("utf-8"))

        elif path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_cors()
            self.end_headers()
            self.wfile.write(b"OK")

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")


if __name__ == "__main__":
    print(f"Starting rāvenS API on port {PORT}...")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Ready! http://localhost:{PORT}/api/members")
    server.serve_forever()
