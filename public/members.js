const BOT_TOKEN = process.env.DISCORD_BOT_TOKEN || "";
const GUILD_ID = process.env.DISCORD_GUILD_ID || "";
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || "*";

const RANK_MAP = {
  "Голова сім'ї":    { rank: "boss",      label: "Голова сім'ї" },
  "Заступник голови":{ rank: "underboss", label: "Заступник голови" },
  "Head Cpt":        { rank: "capo",      label: "Head Cpt" },
  "Dep.Head cpt":    { rank: "capo",      label: "Dep.Head Cpt" },
  "Старший склад":   { rank: "soldier",   label: "Старший склад" },
  "cpt player":      { rank: "soldier",   label: "Cpt Player" },
  "Член сім'ї":      { rank: "member",    label: "Член сім'ї" },
  "Новобранець":     { rank: "associate", label: "Новобранець" },
  "Рекрутер":        { rank: "special",   label: "Рекрутер" },
  "Куратор новачків":{ rank: "special",   label: "Куратор новачків" },
};

const SKIP_ROLES = new Set(["Бот", "carl-bot", "Server Booster", "RAVEN",
  "догана [3/3]", "догана [2/3]", "догана [1/3]"]);

const RANK_ORDER = ["boss", "underboss", "capo", "soldier", "member", "special", "associate"];

async function discordRequest(endpoint) {
  const res = await fetch(`https://discord.com/api/v10${endpoint}`, {
    headers: {
      Authorization: `Bot ${BOT_TOKEN}`,
      "Content-Type": "application/json",
      "User-Agent": "RavensBot/1.0",
    },
  });
  if (!res.ok) return null;
  return res.json();
}

async function getMembers() {
  const rolesData = await discordRequest(`/guilds/${GUILD_ID}/roles`);
  if (!rolesData) return [];
  const roleIdMap = Object.fromEntries(rolesData.map(r => [r.id, r.name]));

  const membersData = await discordRequest(`/guilds/${GUILD_ID}/members?limit=1000`);
  if (!membersData) return [];

  const result = [];
  for (const m of membersData) {
    const user = m.user || {};
    if (user.bot) continue;

    const memberRoles = (m.roles || []).map(id => roleIdMap[id] || "");
    let memberRank = null;

    for (const roleName of memberRoles) {
      if (SKIP_ROLES.has(roleName)) continue;
      if (RANK_MAP[roleName]) {
        const info = RANK_MAP[roleName];
        if (!memberRank || RANK_ORDER.indexOf(info.rank) < RANK_ORDER.indexOf(memberRank.rank)) {
          memberRank = info;
        }
      }
    }

    if (!memberRank) continue;

    let avatarUrl = null;
    if (m.avatar) {
      avatarUrl = `https://cdn.discordapp.com/guilds/${GUILD_ID}/users/${user.id}/avatars/${m.avatar}.png?size=64`;
    } else if (user.avatar) {
      avatarUrl = `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=64`;
    }

    const displayName = m.nick || user.global_name || user.username || "Unknown";

    result.push({
      id: user.id,
      name: displayName,
      username: user.username,
      avatar: avatarUrl,
      rank: memberRank.rank,
      rankLabel: memberRank.label,
      roles: memberRoles.filter(r => r && !SKIP_ROLES.has(r)),
    });
  }

  result.sort((a, b) => RANK_ORDER.indexOf(a.rank) - RANK_ORDER.indexOf(b.rank));
  return result;
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", ALLOWED_ORIGIN);
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Cache-Control", "no-cache");

  if (req.method === "OPTIONS") return res.status(200).end();

  try {
    const members = await getMembers();
    const guildData = await discordRequest(`/guilds/${GUILD_ID}?with_counts=true`);
    const online = guildData?.approximate_presence_count || 0;
    const total = guildData?.approximate_member_count || 0;
    return res.status(200).json({ members, online, total });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
