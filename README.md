# Mobile-friendly NLP Dashboard

A simple, production-oriented Streamlit interface for seven NLP operations:

1. Named-Entity Relationship
2. POS Tagging
3. POS Distribution
4. Lemmatization
5. Stemming
6. Morphology
7. Dependencies (`style="dep"`)

## UX model

The interface intentionally avoids complex tabs and sidebars:

1. Paste text.
2. Press **Analyze text** once.
3. Select one of seven large operation buttons.
4. View only the selected result.

On screens below 700px the action buttons, metrics, and control rows stack into a single column. Dependency diagrams are horizontally swipeable so wide syntax trees do not break mobile layout.

## Local run

```bash
python -m pip install -r requirements.txt
bash run.sh
```

On Windows PowerShell you can instead run:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

## Replit

The repository includes `.replit` and `run.sh`. Import the GitHub repository into Replit and run it. The deployment command listens on `0.0.0.0` and uses Replit's `$PORT`.

### Deploying to Replit Step-by-Step

1. **Create a Replit Account**
   - Go to [replit.com](https://replit.com) and sign up (if you don't have an account)

2. **Import Your GitHub Repository**
   - Click "Create" → "Import from GitHub"
   - Authorize Replit to access your GitHub account
   - Select the `nlp-dashboard` repository
   - Click "Import repository"

3. **Configure the Replit**
   - Replit automatically detects the `.replit` configuration file
   - It will use Python 3.12 as specified in the module section

4. **Install Dependencies**
   - In the Replit shell, run:
     ```bash
     pip install -r requirements.txt
     python -m spacy download en_core_web_sm
     ```

5. **Run the Dashboard**
   - Click the green "Run" button
   - Replit will automatically execute `run.sh` which starts Streamlit
   - A web port will be available in the browser window

6. **Keep Your Replit Alive**
   - Replit instances go to sleep after 24 hours of inactivity
   - To keep it running: Use the [Replit CoDe](https://replit.com/site/codev)
or set up a heartbeat script

7. **Share Your Dashboard**
   - Click the "Share" button
   - Generate a shareable link (e.g., `your-name.nlp-dashboard.replit.app`)
   - Anyone with the link can view and interact with your dashboard

### Replit Deployment Tips

- **Enable Console Access**: Click the terminal icon to monitor logs
- **Manage Resources**: Replit free tier has resource limits; consider upgrading for better performance
- **Backup Your Work**: Regularly push changes back to GitHub

## Deploying to Render Step-by-Step

Render provides free hosting with automatic deployments from GitHub.

### Prerequisites
- A GitHub account with this repository
- A Render account (sign up at [render.com](https://render.com))

### Deployment Steps

1. **Prepare Your Repository**
   - Commit all changes to GitHub:
     ```bash
     git add .
     git commit -m "Add Render deployment configuration"
     git push origin main
     ```
   - Ensure your repository is public or grant Render access

2. **Create a New Web Service on Render**
   - Log in to your Render dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub account
   - Select the `nlp-dashboard` repository

3. **Configure the Service**
   - **Name**: Choose a name (e.g., `nlp-dashboard`)
   - **Region**: Select the region closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave blank (or specify if app is in subdirectory)
   - **Runtime**: Linux
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   
4. **Environment Variables**
   Render automatically sets `$PORT`, but you can add these if needed:
   - `STREAMLIT_SERVER_HEADLESS=true`
   - `STREAMLIT_SERVER_ADDRESS=0.0.0.0`

5. **Deploy**
   - Click "Create Web Service"
   - Render will:
     - Build your application
     - Download spaCy model (included in requirements.txt)
     - Start your dashboard
   - This takes 2-5 minutes

6. **Access Your Dashboard**
   - After deployment, Render displays your live URL
   - Example: `https://nlp-dashboard-xxxx.up.railway.app`
   - Click to open your dashboard

### Render Configuration Files

This project includes:
- **`Procfile`**: Tells Render to run `bash run.sh`
- **`render.yaml`**: Detailed service configuration (alternative to manual setup)

### Using render.yaml (Alternative Method)

Instead of manual configuration, use the `render.yaml` file:

1. Create a new project using the Render CLI or dashboard
2. Choose "Connect existing repository"
3. Render automatically reads `render.yaml` for configuration

### Render Free Tier Limitations

- **Sleep After 15 minutes**: Free web services sleep after 15 minutes of inactivity
- **Wake Up Time**: First request takes ~30 seconds to wake up
- **Storage**: Ephemeral filesystem (no persistent files)
- **Bandwidth**: 100GB/month included

### Keeping Render Active

**Option 1: Upgrade to Paid Plan**
- Pay $7/month for always-on web services

**Option 2: External Health Check**
- Use [UptimeRobot](https://uptimerobot.com/) (free tier)
- Set up monitoring every 5 minutes
- Add your Render URL: `https://your-app.onrender.com/_stcore/health`

**Option 3: Use Railway or Heroku**
- Railway offers generous free tier with no sleep
- Heroku has removed free tier (consider alternatives)

### Customizing Your Deployment

#### For Production Deployment

1. **Update `.streamlit/config.toml`**:
   ```toml
   [server]
   headless = true
   maxUploadSize = 1
   enableXsrfProtection = true
   enableCORS = true
   
   [browser]
   gatherUsageStats = false
   
   [theme]
   primaryColor = "#6B46C1"
   backgroundColor = "#FFFFFF"
   secondaryBackgroundColor = "#F0F2F6"
   textColor = "#26272B"
   fontFamily = "Roboto"
   ```

2. **Add Environment-Specific Settings**:
   - Create a `config.production.toml` for production
   - Include custom domain settings if using a custom domain

3. **Set Up Custom Domain** (Render Pro plan):
   - Go to your service settings
   - Add custom domain
   - Configure DNS records as instructed

### Troubleshooting

#### Build Fails on Render
- Check build logs in Render dashboard
- Verify `requirements.txt` includes all dependencies
- Ensure Python version in `render.yaml` matches your app

#### App Doesn't Load
- Verify `$PORT` environment variable is used
- Check server address binding (`0.0.0.0`)
- Review Streamlit logs in Render dashboard

#### Memory Issues
- Free tier has 512MB RAM limit
- Optimize text input size in `app.py` (MAX_CHARS)
- Consider upgrading to paid plan

## Health Monitor

`.github/workflows/health-check.yml` runs at:

```text
17 and 47 minutes past every hour
```

That is a 30-minute cadence:

```yaml
cron: "17,47 * * * *"
```

Add a GitHub Actions repository secret named `APP_URL` with the deployed Replit URL, for example:

```text
https://your-dashboard.replit.app
```

Do not append `/_stcore/health`; the monitor does that automatically.

Each run checks both:

- `/_stcore/health`
- the public root page

and retries up to five times before failing the workflow.
