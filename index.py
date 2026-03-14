import json
import os
import urllib.request
import urllib.error

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
GUILD_ID = os.environ.get("DISCORD_GUILD_ID", "")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

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

SKIP_ROLES = {"Бот", "carl-bot", "Server Booster", "RAVEN",
              "догана [3/3]", "догана [2/3]", "догана [1/3]"}

RANK_ORDER = ["boss", "underboss", "capo", "soldier", "member", "special", "associate"]


def discord_request(endpoint):
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
    roles_data = discord_request(f"/guilds/{GUILD_ID}/roles")
    if not roles_data:
        return []
    role_id_map = {r["id"]: r["name"] for r in roles_data}
    members_data = discord_request(f"/guilds/{GUILD_ID}/members?limit=1000")
    if not members_data:
        return []

    result = []
    for m in members_data:
        user = m.get("user", {})
        if user.get("bot"):
            continue
        member_rank = None
        member_roles = [role_id_map.get(rid, "") for rid in m.get("roles", [])]
        for role_name in member_roles:
            if role_name in SKIP_ROLES:
                continue
            if role_name in RANK_MAP:
                info = RANK_MAP[role_name]
                if member_rank is None:
                    member_rank = info
                elif RANK_ORDER.index(info["rank"]) < RANK_ORDER.index(member_rank["rank"]):
                    member_rank = info
        if not member_rank:
            continue
        avatar_hash = user.get("avatar") or m.get("avatar")
        if avatar_hash:
            if m.get("avatar"):
                avatar_url = f"https://cdn.discordapp.com/guilds/{GUILD_ID}/users/{user['id']}/avatars/{m['avatar']}.png?size=64"
            else:
                avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{avatar_hash}.png?size=64"
        else:
            avatar_url = None
        display_name = m.get("nick") or user.get("global_name") or user.get("username", "Unknown")
        result.append({
            "id":        user.get("id"),
            "name":      display_name,
            "username":  user.get("username"),
            "avatar":    avatar_url,
            "rank":      member_rank["rank"],
            "rankLabel": member_rank["label"],
            "roles":     [r for r in member_roles if r and r not in SKIP_ROLES],
        })
    result.sort(key=lambda x: RANK_ORDER.index(x["rank"]) if x["rank"] in RANK_ORDER else 99)
    return result


def get_online_status():
    data = discord_request(f"/guilds/{GUILD_ID}?with_counts=true")
    if data:
        return {
            "online": data.get("approximate_presence_count", 0),
            "total":  data.get("approximate_member_count", 0),
        }
    return {"online": 0, "total": 0}


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    cors_headers = [
        ("Access-Control-Allow-Origin", ALLOWED_ORIGIN),
        ("Access-Control-Allow-Methods", "GET, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
        ("Cache-Control", "no-cache"),
    ]

    if method == "OPTIONS":
        start_response("200 OK", cors_headers)
        return [b""]

    if path in ("/api/members", "/"):
        members = get_members()
        counts = get_online_status()
        payload = json.dumps({
            "members": members,
            "online":  counts["online"],
            "total":   counts["total"],
        }, ensure_ascii=False).encode("utf-8")
        start_response("200 OK", cors_headers + [
            ("Content-Type", "application/json; charset=utf-8"),
        ])
        return [payload]

    elif path == "/health":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"OK"]

    else:
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not found"]
