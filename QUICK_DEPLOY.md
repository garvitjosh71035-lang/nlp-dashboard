# Quick Deployment Checklist

## ✅ Pre-Deployment

### Files Created/Modified
- [x] `Procfile` - Added (Render)
- [x] `render.yaml` - Added (Render)
- [x] `requirements.txt` - Updated (removed direct spaCy URL)
- [x] `.gitignore` - Enhanced exclusions
- [x] `README.md` - Expanded with deployment guides
- [x] `DEPLOYMENT_GUIDE.md` - Comprehensive guide created

### Local Testing
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download spaCy model
python -m spacy download en_core_web_sm

# 3. Run locally
streamlit run app.py
# OR on Windows PowerShell:
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Commit Changes
```bash
git add .
git commit -m "Add deployment configuration for Render"
git push origin main
```

---

## 🚀 Deploying to Render

### Step 1: Create Account
- Visit [render.com](https://render.com)
- Sign up with GitHub (recommended)

### Step 2: Create Web Service
1. Click **"New" → "Web Service"**
2. Connect your GitHub repository
3. Select `nlp-dashboard` repo

### Step 3: Configure
| Setting | Value |
|---------|-------|
| Name | `nlp-dashboard` |
| Branch | `main` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` |

### Step 4: Deploy!
- Click **"Create Web Service"**
- Wait 2-5 minutes
- Copy your live URL!

### Step 5: Test
- Open dashboard URL
- Enter sample text
- Check all features work

**Live URL Format**: `https://nlp-dashboard-xxxx.up.railway.app`

---

## 💻 Deploying to Replit

### Step 1: Import Repository
1. Visit [replit.com](https://replit.com)
2. Click **"Create" → "Import from GitHub"**
3. Select `nlp-dashboard` repo
4. Click **"Import"**

### Step 2: Install Dependencies
In Replit shell:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 3: Run!
- Click green **"Run"** button
- Dashboard opens automatically
- Click **"Share"** to get link

**Replit URL Format**: `your-name.nlp-dashboard.replit.app`

### Step 4: Keep Alive (Optional)
- Use UptimeRobot to ping every 5 minutes
- Or pay for premium membership

---

## ⚠️ Common Issues

### Build Fails on Render
**Fix**: Check Python version, verify all packages in requirements.txt

### App Won't Load
**Fix**: Ensure `$PORT` is used, bind to `0.0.0.0`

### Sleeps After 15 Minutes (Render Free)
**Fix**: 
- Option A: Use UptimeRobot (free)
- Option B: Upgrade to $7/mo plan
- Option C: Accept cold starts

### Memory Errors
**Fix**: Reduce MAX_CHARS, optimize processing, upgrade plan

---

## 📊 Cost Comparison

| Platform | Free Tier | Paid Plan | Best For |
|----------|-----------|-----------|----------|
| **Render** | 1 build/hr, sleeps after 15min | $7/mo always-on | Production apps |
| **Replit** | Limited runtime | $5-15/mo | Learning/demos |

**Recommendation**: Use Render free tier with uptime monitoring OR pay for always-on

---

## 🔄 Automatic Updates

Both platforms support auto-deployment:
- Push to `main` branch
- Platforms detect change
- Automatically rebuild and redeploy
- No manual intervention needed!

---

## 📝 Summary Commands

### Local Development
```powershell
# Windows PowerShell
pip install -r requirements.txt
streamlit run app.py
```

```bash
# Bash/Linux/Mac
pip install -r requirements.txt
bash run.sh
```

### Deploy Check
```bash
# Verify everything works locally first
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); doc = nlp('Test sentence'); print('spaCy loaded:', len(doc))"
```

---

## 🆘 Need Help?

- **Full Guide**: See `DEPLOYMENT_GUIDE.md`
- **Render Docs**: https://render.com/docs
- **Streamlit Docs**: https://docs.streamlit.io
- **Community**: Stack Overflow, Reddit

---

## ✨ Quick Reference

**Files you need:**
- `app.py` - Main application
- `run.sh` - Launch script (uses $PORT env var)
- `Procfile` - Render process config
- `render.yaml` - Detailed Render config
- `.streamlit/config.toml` - Streamlit settings

**Key Environment Variables:**
- `$PORT` - Set by platform automatically ✓
- `STREAMLIT_SERVER_HEADLESS=true` - Optional
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0` - Optional

**Testing URLs:**
- Health check: `https://your-app.onrender.com/_stcore/health`
- Public page: `https://your-app.onrender.com/`

---

**Ready? Start now!** 🎯
