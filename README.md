# ☠ rāvenS — GTA V Family Site (з Discord інтеграцією)

## 🗂 Структура

```
ravens-full/
├── api/
│   └── server.py       ← Python бекенд (Discord API)
├── public/
│   ├── index.html
│   ├── style.css
│   ├── config.js       ← РЕДАГУЙ ЦЕЙ ФАЙЛ
│   ├── particles.js
│   └── discord.js
├── Procfile            ← для Railway/Render
├── requirements.txt
└── README.md
```

---

## 🚀 Запуск локально

### 1. Запусти бекенд
```bash
python api/server.py
```
Бекенд запуститься на http://localhost:8000

### 2. Відкрий сайт
Відкрий `public/index.html` у браузері.

Сайт автоматично підтягне учасників з твого Discord сервера!

---

## ☁️ Деплой на Railway (безкоштовно)

1. Зареєструйся на https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Завантаж цю папку на GitHub, підключи репо
4. Railway автоматично запустить `python api/server.py`
5. Скопіюй URL який дасть Railway (типу `https://ravens-xxx.up.railway.app`)
6. Встав цей URL в `public/config.js` → поле `apiUrl`
7. Задеплой `public/` папку на Vercel окремо

### Або деплой API на Render:
1. https://render.com → "New Web Service"
2. Підключи GitHub репо
3. Build Command: (порожньо)
4. Start Command: `python api/server.py`
5. Скопіюй URL → встав в `config.js`

---

## ⚙️ Налаштування config.js

```js
const CONFIG = {
  apiUrl: "https://твій-api.up.railway.app", // URL бекенду після деплою
  discordInvite: "https://discord.gg/...",   // Посилання на сервер
  discordServerId: "1465060634696749231",     // Server ID
  stats: {
    weeklyEarn: "$4.8M",
    heistsDone: 128,
    founded: "Jan 2026"
  }
};
```

---

## 🎭 Ранги (автоматично з ролей Discord)

| Роль Discord       | Ранг на сайті |
|--------------------|---------------|
| Голова сім'ї       | Boss          |
| Заступник голови   | Underboss     |
| Head Cpt           | Capo          |
| Dep.Head cpt       | Capo          |
| Старший склад      | Soldier       |
| cpt player         | Soldier       |
| Член сім'ї         | Member        |
| Новобранець        | Associate     |
| Рекрутер           | Special       |
| Куратор новачків   | Special       |

Боти, carl-bot, Server Booster — автоматично приховані.
