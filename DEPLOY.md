# 🚀 Deploy AI Home Tutor to the Web

Deploy your AI Home Tutor to **tutor.theaihublab.com** using:

- **Render.com** — hosts the Streamlit app (free tier works)
- **Supabase** — Postgres database for persistent data
- **Hostinger cPanel** — DNS for your subdomain
- **Google Gemini** — the AI brain

Follow these steps in order. Total time: ~30 minutes.

---

## Step 1 — Get your Gemini API key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google.
3. Click **Create API key** → choose a project (or create a new one).
4. Copy the key — it starts with `AIza...`
5. Keep it handy (you'll paste it into Render in Step 4).

---

## Step 2 — Set up Supabase (the database)

1. Go to https://supabase.com → sign in.
2. Click **New project**.
   - Name: `ai-tutor`
   - Database password: pick a strong one and **save it**
   - Region: pick the one closest to you (e.g., `ap-south-1` for India)
3. Wait ~2 minutes for the project to spin up.
4. Go to **Project Settings → Database → Connection string**.
5. Select the **URI** tab.
6. Copy the connection string — it looks like:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
   ```
7. Replace `[YOUR-PASSWORD]` with the password you set in step 2.
8. Save this full string — you'll paste it into Render in Step 4.

> **Tip:** Use the **Transaction pooler** (port `6543`), not the direct connection. It handles Render's free-tier networking better.

---

## Step 3 — Push the project to GitHub

Render pulls your code from GitHub. So:

1. Go to https://github.com → **New repository**.
   - Name: `ai-tutor-web`
   - Visibility: **Private** (recommended)
   - Don't add README/license (project already has what's needed)
2. On your computer, open a terminal in the `ai-tutor-web` folder and run:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/ai-tutor-web.git
   git push -u origin main
   ```

   Replace `YOUR-USERNAME` with your GitHub username.

> If you've never used Git, install [GitHub Desktop](https://desktop.github.com/) — it does the same thing by clicking buttons.

---

## Step 4 — Deploy on Render.com

1. Go to https://render.com → sign in with GitHub.
2. Click **New +** → **Web Service**.
3. Connect the `ai-tutor-web` repository.
4. Fill in:
   - **Name:** `ai-tutor-web` (this becomes `ai-tutor-web.onrender.com`)
   - **Region:** pick one close to you
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```
     streamlit run main.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection true
     ```
   - **Plan:** Free
5. Click **Advanced** and add these **Environment Variables**:

   | Key             | Value                                                                                  |
   | --------------- | -------------------------------------------------------------------------------------- |
   | `DATABASE_URL`  | Your full Supabase URI from Step 2 (with the real password)                            |
   | `GEMINI_API_KEY`| Your Gemini key from Step 1 (starts with `AIza…`)                                      |
   | `GEMINI_MODEL`  | `gemini-2.5-flash` *(optional — default is already this)*                              |
   | `PYTHON_VERSION`| `3.11.9`                                                                               |

6. Click **Create Web Service**. Render will build and deploy (~3–5 minutes).
7. When it says **Live**, open `https://ai-tutor-web.onrender.com` — the app should load.

> **Free tier note:** Render's free tier sleeps after 15 minutes of inactivity and takes ~30 seconds to wake up on the first visit. For a paid instant-wake instance, upgrade to Starter ($7/mo).

---

## Step 5 — Point your subdomain `tutor.theaihublab.com` at Render

### 5a. Add the custom domain in Render

1. In your Render service, go to **Settings → Custom Domains**.
2. Click **Add Custom Domain**.
3. Enter: `tutor.theaihublab.com`
4. Render shows you a **CNAME target** like:
   ```
   ai-tutor-web.onrender.com
   ```
   Copy this exact value.

### 5b. Add the CNAME record in Hostinger cPanel

1. Log into **Hostinger hPanel**.
2. Go to **Domains → theaihublab.com → DNS / Name Servers** (or **Advanced → Zone Editor** if you're in cPanel-classic).
3. Click **Add Record** / **Manage DNS records** → **Add Record**.
4. Fill in:
   - **Type:** `CNAME`
   - **Name:** `tutor`   *(this will make it `tutor.theaihublab.com`)*
   - **Target / Points to:** `ai-tutor-web.onrender.com`   *(the value from Render)*
   - **TTL:** `14400` (or default)
5. Save.

> If Hostinger warns "a record already exists for `tutor`" — delete the existing A/CNAME record first, then add the new CNAME.

### 5c. Wait for DNS + verify in Render

1. DNS usually propagates in 5–30 minutes (sometimes up to a few hours).
2. Go back to Render → **Settings → Custom Domains**.
3. Render auto-checks — it will show **Verified** and issue a free SSL certificate.
4. Visit `https://tutor.theaihublab.com` — your AI Tutor is live! 🎓

---

## Step 6 — First-use setup

1. Open `https://tutor.theaihublab.com`.
2. Go to **⚙️ Settings → 👤 Student Profile** — set your child's name, age, avatar.
3. In **🤖 AI Settings** you'll see "Gemini API key is configured on the server" (because you set `GEMINI_API_KEY` on Render). You don't need to paste it again.
4. Start using the app!

---

## Troubleshooting

**Render build fails with "psycopg2 error"**
- Make sure `requirements.txt` has `psycopg2-binary` (not `psycopg2`). It does by default in this repo.

**App loads but says "Basic Mode / no API key"**
- Check Render → Environment → `GEMINI_API_KEY` is set and starts with `AIza`.
- Redeploy: Render → **Manual Deploy → Clear build cache & deploy**.

**Data doesn't persist / progress resets**
- Check Render → Environment → `DATABASE_URL` is set and starts with `postgresql://`.
- Check Supabase → **Table Editor** — you should see tables (`student`, `quiz_results`, etc.) after the first app load.

**Subdomain won't verify in Render**
- Check the CNAME in Hostinger points to the exact target Render gave you.
- Try `nslookup tutor.theaihublab.com` in a terminal — it should return the Render target.
- Wait longer — some DNS providers take up to 24 hours.

**Free tier too slow on first load**
- Normal. Upgrade to Render Starter ($7/mo) to keep the service always-on.

---

## Local development

To test on your computer before pushing changes:

1. Copy `.env.example` to `.env`
2. Fill in `DATABASE_URL` (you can use your Supabase URL, or leave blank to use local SQLite)
3. Fill in `GEMINI_API_KEY`
4. Run:
   ```bash
   pip install -r requirements.txt
   streamlit run main.py
   ```
5. Open http://localhost:8501

---

## Updating the deployed app

Any push to your GitHub `main` branch auto-deploys to Render (because `autoDeploy: true` is in `render.yaml`). So just:

```bash
git add .
git commit -m "Your change"
git push
```

Render rebuilds automatically in 2–3 minutes.
