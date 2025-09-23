# 🚀 AAGAMI RAIL DEPLOYMENT GUIDE
## **Multiple Platform Deployment Options**

---

## 🎯 **RECOMMENDED: REPLIT (Full-Stack - EASIEST)**

### **✅ Why Replit is Perfect:**
- **Full-stack support** (FastAPI + React + MongoDB)
- **Zero configuration** deployment
- **Built-in database** hosting
- **Live collaboration** for hackathon demos
- **Instant sharing** with judges via URL

### **🚀 Replit Deployment Steps (15 minutes):**

#### **Step 1: Prepare Files**
```bash
# Create Replit configuration files
```

**Create `.replit` file:**
```toml
modules = ["python-3.11", "nodejs-18"]

[nix]
channel = "stable-22_11"

[[ports]]
localPort = 3000
externalPort = 80

[[ports]]
localPort = 8001
externalPort = 3001

[deployment]
run = ["sh", "-c", "python backend/server.py & cd frontend && npm start"]
deploymentTarget = "cloudrun"
```

**Create `replit.nix` file:**
```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.nodejs_18
    pkgs.yarn
    pkgs.mongodb
  ];
}
```

#### **Step 2: Backend Setup for Replit**
**Update `backend/server.py`:**
```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn

app = FastAPI()

# CORS for Replit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Replit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection for Replit
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.aagami_rail

# ... rest of your FastAPI code ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### **Step 3: Frontend Setup for Replit**
**Update `frontend/.env`:**
```env
REACT_APP_BACKEND_URL=https://your-repl-name.your-username.repl.co:3001
```

**Update `frontend/package.json`:**
```json
{
  "scripts": {
    "start": "BROWSER=none react-scripts start",
    "build": "react-scripts build"
  }
}
```

#### **Step 4: Deploy to Replit**
1. **Go to Replit.com** and create new Repl
2. **Import from GitHub** or drag & drop files
3. **Install dependencies:**
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend  
   cd frontend && yarn install
   ```
4. **Set environment variables** in Replit Secrets:
   - `MONGO_URL`: Your MongoDB connection string
   - `JWT_SECRET`: Your JWT secret key
5. **Run the application** - Replit auto-detects and runs both services
6. **Share the URL** with hackathon judges!

---

## 🌐 **VERCEL (Frontend) + Railway (Backend)**

### **✅ Why This Combo:**
- **Vercel**: Lightning-fast React deployment
- **Railway**: Easy Python backend hosting
- **MongoDB Atlas**: Cloud database
- **Professional URLs** and performance

### **🚀 Deployment Steps (20 minutes):**

#### **Step 1: Deploy Backend to Railway**
1. **Go to Railway.app** and connect GitHub
2. **Deploy from GitHub repo**
3. **Add environment variables:**
   ```env
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/aagami_rail
   JWT_SECRET=your-secret-key
   PORT=8001
   ```
4. **Railway auto-deploys** FastAPI backend
5. **Copy the Railway URL** (e.g., `https://backend-production-xxx.up.railway.app`)

#### **Step 2: Deploy Frontend to Vercel**
**Update `frontend/.env.production`:**
```env
REACT_APP_BACKEND_URL=https://backend-production-xxx.up.railway.app
```

**Deploy to Vercel:**
1. **Install Vercel CLI:** `npm i -g vercel`
2. **Deploy frontend:**
   ```bash
   cd frontend
   vercel --prod
   ```
3. **Set build settings:**
   - Build Command: `yarn build`
   - Output Directory: `build`
   - Install Command: `yarn install`

#### **Step 3: MongoDB Atlas Setup**
1. **Create MongoDB Atlas account** (free tier)
2. **Create cluster** and database
3. **Get connection string**
4. **Update Railway environment variables**

---

## 📦 **NETLIFY (Frontend) + Heroku (Backend)**

### **🚀 Quick Deployment:**

#### **Backend to Heroku:**
**Create `Procfile`:**
```
web: uvicorn backend.server:app --host 0.0.0.0 --port $PORT
```

**Deploy:**
```bash
# Install Heroku CLI
heroku create aagami-rail-backend
git subtree push --prefix backend heroku main
heroku config:set MONGO_URL=your-mongodb-url
```

#### **Frontend to Netlify:**
1. **Drag & drop `frontend/build`** folder to Netlify
2. **Or connect GitHub** for auto-deployment
3. **Set environment variables** in Netlify dashboard

---

## ⚡ **FASTEST OPTION: Replit One-Click Deploy**

### **🎯 Complete Replit Setup Script:**

**Create `deploy.sh`:**
```bash
#!/bin/bash
echo "🚀 Setting up AAGAMI RAIL for Replit..."

# Install backend dependencies
cd backend
pip install fastapi uvicorn motor pymongo python-jose passlib python-multipart

# Install frontend dependencies  
cd ../frontend
yarn install

# Build frontend for production
yarn build

echo "✅ Setup complete! Run 'python backend/server.py' to start"
```

**Create `run.sh`:**
```bash
#!/bin/bash
# Start backend
cd backend && python server.py &

# Start frontend
cd frontend && yarn start &

# Keep script running
wait
```

### **🎪 Replit Demo Features:**
```python
# Add to backend/server.py for Replit demos
@app.get("/demo/reset")
async def reset_demo():
    """Reset demo data for hackathon presentation"""
    await db.trains.delete_many({})
    await db.disasters.delete_many({})
    # Reload sample data
    for train in SAMPLE_TRAINS:
        await db.trains.insert_one(train.dict())
    return {"message": "Demo reset successfully"}

@app.get("/demo/status")
async def demo_status():
    """Show system status for judges"""
    return {
        "status": "operational",
        "trains_count": await db.trains.count_documents({}),
        "active_disasters": await db.disasters.count_documents({"resolved": False}),
        "api_version": "1.0",
        "demo_mode": True
    }
```

---

## 🏆 **HACKATHON-SPECIFIC DEPLOYMENT**

### **🎯 Judge-Ready Features:**

#### **Environment Variables for All Platforms:**
```env
# Backend (.env)
MONGO_URL=mongodb://localhost:27017  # Or Atlas URL
JWT_SECRET=hackathon-demo-secret-key
DEMO_MODE=true
API_VERSION=1.0

# Frontend (.env)
REACT_APP_BACKEND_URL=https://your-backend-url
REACT_APP_DEMO_MODE=true
REACT_APP_VERSION=1.0
```

#### **Demo Reset Endpoint:**
```python
@app.post("/api/demo/quick-scenario")
async def quick_demo_scenario(scenario: str):
    """Quick demo scenarios for judges"""
    scenarios = {
        "normal": {"trains": 10, "disasters": 0},
        "conflict": {"trains": 15, "disasters": 0, "conflicts": 5},
        "disaster": {"trains": 10, "disasters": 2},
        "scale": {"trains": 100, "disasters": 1}
    }
    
    # Reset and load scenario data
    await reset_database()
    await load_scenario_data(scenarios[scenario])
    
    return {"message": f"Demo scenario '{scenario}' loaded"}
```

---

## 📱 **MOBILE-RESPONSIVE DEPLOYMENT**

### **Frontend Optimizations:**
```javascript
// Add to frontend/src/index.js
if (process.env.REACT_APP_DEMO_MODE === 'true') {
  // Add demo-specific configurations
  console.log('🎪 AAGAMI RAIL - Hackathon Demo Mode Active');
  
  // Add demo data refresh every 30 seconds
  setInterval(() => {
    // Refresh demo data
  }, 30000);
}
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment:**
- [ ] Update CORS settings for production URLs
- [ ] Set environment variables for all services
- [ ] Test API endpoints with production URLs
- [ ] Verify database connectivity
- [ ] Test frontend-backend communication

### **Post-Deployment:**
- [ ] Verify all routes work correctly
- [ ] Test optimization functionality
- [ ] Test disaster management features
- [ ] Check map visualization
- [ ] Confirm mobile responsiveness

### **Hackathon Demo Ready:**
- [ ] Demo reset endpoint working
- [ ] Quick scenario loading functional
- [ ] All interactive features responsive
- [ ] Performance metrics displaying correctly
- [ ] Judge demo controller operational

---

## 🎯 **RECOMMENDED FOR HACKATHON:**

### **🥇 Best Option: Replit**
- **Pros:** Full-stack, easy setup, live collaboration, instant sharing
- **Cons:** Slight performance limitations
- **Perfect for:** Live demos, judge presentations, team collaboration

### **🥈 Alternative: Vercel + Railway**
- **Pros:** Professional performance, separate scaling, custom domains
- **Cons:** More complex setup, requires multiple accounts
- **Perfect for:** Production-ready deployments, impressive performance

### **🥉 Quick Demo: Netlify Drop**
- **Pros:** Instant frontend deployment
- **Cons:** Backend requires separate hosting
- **Perfect for:** Frontend-only demos, quick sharing

**Choose Replit for the easiest hackathon demo experience! 🚄✨**