# Deployment Guide

## 🚀 Quick Deploy to Production

### Backend Deployment (Render - Recommended)

1. **Create Account** at [render.com](https://render.com)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure Service**
   - **Name**: `ai-interview-prep-backend` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**
   - Add `OPENAI_API_KEY` = your OpenAI API key

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment
   - Copy the URL (e.g., `https://your-app.onrender.com`)

6. **Update CORS** (if needed)
   - In `main.py`, add your frontend URL to `allow_origins`

### Frontend Deployment (Vercel - Recommended)

1. **Create Account** at [vercel.com](https://vercel.com)

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import from GitHub
   - Select your repository

3. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. **Environment Variables**
   - Add `VITE_API_URL` = your backend URL from Render

5. **Deploy**
   - Click "Deploy"
   - Your app will be live at `your-project.vercel.app`

### Alternative: Railway (Backend)

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select repository
4. Set root directory to `backend`
5. Add `OPENAI_API_KEY` environment variable
6. Railway auto-detects Python/FastAPI

## 📝 Step-by-Step Instructions

### Step 1: Prepare Your Code

```bash
# Make sure everything is committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy Backend First

1. Deploy backend on Render (follow steps above)
2. Wait for deployment to complete
3. Test the API: `https://your-backend.onrender.com/`
4. Should see: `{"message": "AI Interview Prep Tool API", ...}`

### Step 3: Deploy Frontend

1. Deploy frontend on Vercel
2. Use backend URL in `VITE_API_URL`
3. Wait for deployment
4. Test the full application

### Step 4: Update CORS

Edit `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-frontend.vercel.app",  # Add this
        "https://leboid.github.io"  # Add your portfolio domain
    ],
    ...
)
```

Redeploy backend after CORS update.

## 🔧 Environment Variables Summary

### Backend (.env or Render Environment)
```
OPENAI_API_KEY=sk-...
```

### Frontend (Vercel Environment)
```
VITE_API_URL=https://your-backend.onrender.com
```

## 🌐 Custom Domain (Optional)

### Vercel
1. Project Settings → Domains
2. Add domain
3. Update DNS records as instructed

### Render
1. Settings → Custom Domains
2. Add domain
3. Update DNS

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Backend deployed on Render/Railway
- [ ] Backend URL tested and working
- [ ] `OPENAI_API_KEY` set
- [ ] Frontend deployed on Vercel
- [ ] `VITE_API_URL` set to backend URL
- [ ] CORS updated in backend
- [ ] Full app tested end-to-end
- [ ] Mobile responsiveness checked

## 🐛 Troubleshooting

### Backend Issues
- **502 Bad Gateway**: Check if backend is running, check logs
- **Environment variables not working**: Make sure they're set in Render dashboard
- **CORS errors**: Update `allow_origins` in `main.py`

### Frontend Issues
- **API calls failing**: Check `VITE_API_URL` is correct
- **Build fails**: Check Node version (18+), check for errors in logs
- **404 on routes**: Check `_redirects` file in `public/` folder

## 💰 Free Tier Limits

- **Render Free Tier**: 
  - Spins down after 15 min of inactivity
  - 750 hours/month free
  - $7/month to keep always on

- **Vercel Free Tier**: 
  - Unlimited for personal projects
  - 100GB bandwidth/month

- **OpenAI API**: 
  - Pay per use
  - ~$0.01-0.02 per interview session
  - Set usage limits in OpenAI dashboard

## 📊 Monitoring

Check logs in:
- **Render**: Dashboard → Your Service → Logs
- **Vercel**: Project → Deployments → Click deployment → Functions/Logs

---

Need help? Check the main README or open an issue!

