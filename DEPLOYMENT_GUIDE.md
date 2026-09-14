# Deployment Guide for NLP Dashboard

This guide provides step-by-step instructions for deploying your NLP Dashboard to **Render** and **Replit**.

---

## Quick Summary

### Files Added for Deployment

1. **`Procfile`**: Tells Render how to run your app
2. **`render.yaml`**: Detailed Render service configuration
3. **Updated `requirements.txt`**: Removed direct spaCy model URL (now handled automatically)
4. **Updated `.gitignore`**: Better exclusions for production
5. **Updated `README.md`**: Comprehensive deployment instructions

---

## Part 1: Deploying to Render

### What is Render?

Render is a cloud platform that makes it easy to deploy web apps, APIs, and databases. They offer:
- Free tier for hobby projects
- Automatic deployments from GitHub
- HTTPS out of the box
- Easy scaling options

### Prerequisites

- A GitHub account with this repository
- A Render account (free at [render.com](https://render.com))
- Git installed locally (optional)

### Step-by-Step Render Deployment

#### Method 1: Using Render Dashboard (Recommended for Beginners)

1. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration files"
   git push origin main
   ```

2. **Log in to Render**
   - Go to [render.com](https://render.com)
   - Click "Get Started for Free"
   - Sign up using GitHub (recommended for quick setup)

3. **Create a New Web Service**
   - Click the **"New"** button in the top right
   - Select **"Web Service"**
   - Click **"Connect a repository"**
   - Find and select your `nlp-dashboard` repository
   - Click **"Connect"**

4. **Configure Your Service**
   Render will auto-detect many settings, but verify:
   - **Name**: `nlp-dashboard` (or whatever you prefer)
   - **Region**: Choose closest to your users (e.g., US Eastern Europe)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (app is in root)
   - **Runtime**: Linux
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

5. **Environment Variables (Optional)**
   Render automatically provides `$PORT`. You can skip these, or add:
   - `STREAMLIT_SERVER_HEADLESS` = `true`
   - `STREAMLIT_SERVER_ADDRESS` = `0.0.0.0`

6. **Deploy!**
   - Scroll down and click **"Create Web Service"**
   - Wait 2-5 minutes while Render builds and deploys
   - You'll see build logs in real-time

7. **Access Your App**
   - Once deployment succeeds, you'll see your live URL
   - Format: `https://nlp-dashboard-xxxx.railway.app`
   - Click it to open your dashboard!

#### Method 2: Using render.yaml (Advanced)

If you prefer declarative configuration:

1. The `render.yaml` file is already included in your repo
2. In Render dashboard, choose **"New" → "Project"**
3. Click **"Add New Web Service"**
4. Upload `render.yaml` manually OR select "Import from GitHub" and Render will read it automatically
5. Follow similar steps as above

### Understanding the Configuration Files

#### Procfile
```
web: bash run.sh
```
Simple instruction: When Render runs the `web` process, execute `run.sh`.

#### render.yaml
Detailed YAML configuration including:
- Build commands (dependencies installation)
- Start commands (how to launch the app)
- Environment variables (configuration)
- Python version specification

#### Why we removed en-core-web-sm from requirements.txt
Instead of downloading via URL (which sometimes fails), Render's environment includes spacy properly, so our code downloads it cleanly during initialization.

### Common Render Issues & Solutions

#### Issue: Build Fails
**Symptoms**: Red error messages in build log

**Solutions**:
1. Check Python version compatibility in `render.yaml`
2. Verify all dependencies are in `requirements.txt`
3. Look for outdated package versions
4. Try building locally first: `pip install -r requirements.txt`

#### Issue: App Starts But Won't Load
**Symptoms**: Blank page, connection timeout

**Solutions**:
1. Verify `$PORT` env var is being used
2. Check that server binds to `0.0.0.0`, not `localhost`
3. Review app logs in Render dashboard
4. Test with minimal Streamlit app first

#### Issue: Free Tier Sleeps After 15 Minutes
**Symptoms**: First request after idle time takes 30+ seconds

**Solutions**:
1. Use UptimeRobot to ping every 5 minutes (free)
2. Upgrade to paid plan ($7/month)
3. Accept cold start delay if infrequent usage

#### Issue: Memory Errors
**Symptoms**: Process killed, OOM errors

**Solutions**:
1. Reduce MAX_CHARS in `app.py`
2. Optimize text processing logic
3. Upgrade to paid plan (higher RAM limits)

---

## Part 2: Deploying to Replit

### What is Replit?

Replit is an online IDE and hosting platform perfect for:
- Learning and prototyping
- Small personal projects
- Collaborative development
- Quick demos

### Prerequisites

- A Replit account (free at [replit.com](https://replit.com))
- This code in a GitHub repository (public recommended)

### Step-by-Step Replit Deployment

#### Method 1: Import from GitHub

1. **Create a Replit Account**
   - Visit [replit.com](https://replit.com)
   - Sign up with Google/GitHub/Email

2. **Import Repository**
   - Click the **"Create"** button
   - Select **"Import from GitHub"**
   - Authorize Replit access to GitHub
   - Find and select your `nlp-dashboard` repository
   - Click **"Import repository"**

3. **Install Dependencies**
   In the Replit shell/console:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
   ⚠️ Note: Installing spaCy models might take extra time

4. **Configure Run Settings**
   - Replit reads `.replit` configuration automatically
   - It should use Python 3.12 as specified
   - No manual changes needed usually

5. **Run Your App**
   - Click the big green **"Run"** button (top center)
   - Replit executes `run.sh` which starts Streamlit
   - A browser window opens with your dashboard

6. **Get Shareable Link**
   - Click **"Share"** button (top right)
   - Generate public link (format: `your-name.nlp-dashboard.replit.app`)
   - Share with anyone!

#### Method 2: Manual Setup

If importing has issues:

1. Create new Replit project manually
2. Copy-paste all files from your GitHub repo
3. Install dependencies manually
4. Configure `.replit` as shown below

### Keeping Your Replit Active

#### Problem: Goes to Sleep After 24 Hours

**Solution 1: Use CoDe Bot (Free)**
- Join [Replit's CoDe bot](https://replit.com/site/codev)
- Set up automated pings to keep alive

**Solution 2: External Ping Service**
- Use [UptimeRobot](https://uptimerobot.com/)
- Ping your Replit URL every 5 minutes
- Free tier available

**Solution 3: Premium Membership**
- Pay for Replit Infinity
- Longer uptime guarantees

### Replit-Specific Tips

#### Access Logs
- Click terminal icon to view console output
- Real-time debugging capability

#### Resource Management
- Free tier: Limited CPU/RAM
- Consider upgrading for heavy NLP tasks

#### Version Control
- Push changes back to GitHub regularly
- `git pull` on Replit to sync external changes

#### File Limits
- Replit has storage quotas
- Don't store large temporary files

---

## Part 3: Testing & Validation

### Before Deployment

1. **Test Locally First**
   ```bash
   streamlit run app.py
   ```
   Ensure everything works on your machine

2. **Check File Structure**
   ```
   nlp-dashboard/
   ├── app.py ✓
   ├── nlp_engine.py ✓
   ├── ui.py ✓
   ├── requirements.txt ✓
   ├── run.sh ✓
   ├── .streamlit/config.toml ✓
   ├── Procfile ✓
   └── render.yaml ✓
   ```

3. **Verify Dependencies**
   ```bash
   pip install -r requirements.txt
   python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"
   ```

### After Deployment

#### Health Checks
- Visit your deployed URL
- Enter sample text
- Test all 7 NLP operations
- Download results to verify data integrity

#### Monitoring
- **Render**: Dashboard → Metrics tab
- **Replit**: Console → Performance metrics
- Set up alerts for downtime

#### Error Tracking
Enable logging to catch issues early:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## Part 4: Post-Deployment Customization

### Adding a Custom Domain (Render Pro)

1. Go to your Render dashboard
2. Select your service
3. Click **"Settings"** → **"Custom Domains"**
4. Add your domain (e.g., `nlp.yourdomain.com`)
5. Update DNS records as instructed
6. SSL certificate auto-provisioned

### Updating Configuration

#### Production Settings (`.streamlit/config-production.toml`)
```toml
[theme]
primaryColor = "#6B46C1"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#26272B"
fontFamily = "Roboto"

[browser]
gatherUsageStats = false

[server]
headless = true
maxUploadSize = 10
enableXsrfProtection = true
```

### Adding Authentication (Future Enhancement)

For protected dashboards:
```python
# In app.py
import os

api_key = os.environ.get("DASHBOARD_API_KEY")

def check_auth():
    if api_key:
        provided = st.text_input("API Key", type="password")
        return provided == api_key
    return True

if check_auth():
    # Show dashboard
```

---

## Part 5: Cost Comparison

### Render Pricing

| Plan | Cost | Features |
|------|------|----------|
| Free | $0 | 1 build/hr, sleeps after 15min idle |
| Standard | $7/mo | Always-on, faster builds |
| Pro | $15/mo | More resources, custom domains |

### Replit Pricing

| Plan | Cost | Features |
|------|------|----------|
| Free | $0 | Limited runtime, community support |
| Hacker | $5/mo | Longer sessions, priority |
| Pro | $15/mo | Max resources, premium features |

### Recommendation by Use Case

**Choose Render if:**
- ✅ Need production-grade reliability
- ✅ Want automatic updates from GitHub
- ✅ Expect occasional user traffic
- ✅ Need custom domains eventually

**Choose Replit if:**
- ✅ Building for learning/testing
- ✅ Small personal project only
- ✅ Want collaborative features
- ✅ Prefer visual IDE interface

---

## Troubleshooting Cheat Sheet

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Build fails | Missing dependency | Check requirements.txt |
| App won't load | Port binding issue | Use $PORT variable |
| Slow startup | Model loading | Cache model with @st.cache_resource |
| Memory error | Too much text | Reduce MAX_CHARS limit |
| 404 errors | Wrong path | Verify route configuration |
| 502/503 errors | Server overloaded | Upgrade plan, optimize code |

---

## Next Steps

After successful deployment:

1. ✅ Test all features thoroughly
2. ✅ Share with team/users
3. ✅ Monitor performance metrics
4. ✅ Set up health checks (existing workflow)
5. ✅ Plan for scaling if traffic grows
6. ✅ Backup critical configurations
7. ✅ Document any customizations

---

## Support Resources

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **spaCy Docs**: [spacy.io/docs](https://spacy.io/docs)
- **NLP Community**: Stack Overflow, Reddit r/MachineLearning

---

**Ready to deploy?** Start with Render for production, Replit for development! 🚀
