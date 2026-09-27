Auto-Forward-Test-main/              ← 🏠 ROOT FOLDER
│
├── 📂 plugins/                      ← Saare command handlers
│   ├── __init__.py                  ← (khali file - agar nahi hai toh banao)
│   ├── broadcast.py                 ← Broadcast commands
│   ├── commands.py                  ← Basic commands (/start, /help, etc.)
│   ├── db.py                        ← DB helper commands
│   ├── owner_panel.py               ← ⭐ ADMIN PANEL (colorful buttons)
│   ├── premium.py                   ← ⭐ PREMIUM system (/myplan, /addpremium)
│   ├── public.py                    ← Public forward (bot)
│   ├── regix.py                     ← 🔥 MAIN FORWARDING ENGINE (limit check yahan)
│   ├── settings.py                  ← /settings command
│   ├── test.py                      ← Test commands
│   ├── unequify.py                  ← Duplicate delete
│   └── utils.py                     ← Helper utilities
│
├── 📄 .python-version               ← Python version (runtime)
├── 📄 app.py                        ← Flask app (Koyeb health check)
├── 📄 config.py                     ← ⚙️ API_ID, BOT_TOKEN, OWNER, PREMIUM settings
├── 📄 database.py                   ← 💾 MongoDB (users, premium, usage)
├── 📄 Dockerfile                    ← Docker deploy config
├── 📄 helper.py                     ← ⭐ can_forward() / consume_forward()
├── 📄 LICENCE                       ← License file
├── 📄 main.py                       ← 🚀 Bot entry point
├── 📄 Procfile                      ← Deploy process file
├── 📄 README.md                     ← Documentation
├── 📄 requirements.txt              ← Python dependencies
├── 📄 run cmd.txt                   ← Run command (gunicorn + main.py)
└── 📄 script.py                     ← 📝 All text templates
