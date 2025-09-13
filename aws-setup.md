# AWS EC2 Deployment Guide

## 🏗️ **Instance Configuration**

### **Recommended Instance: t4g.nano**
- **Instance Type:** t4g.nano
- **vCPUs:** 2 (burstable)
- **Memory:** 0.5 GB (512 MB)
- **Storage:** 8 GB gp3
- **Cost:** ~$3.04/month (us-east-1)
- **OS:** Ubuntu 22.04 LTS

### **Alternative: t3.nano**
- **Instance Type:** t3.nano
- **vCPUs:** 2 (burstable)
- **Memory:** 0.5 GB (512 MB)
- **Cost:** ~$3.80/month (us-east-1)

## 🚀 **Step-by-Step Setup**

### **1. Launch EC2 Instance**
1. Go to AWS Console → EC2
2. Click "Launch Instance"
3. Choose "Ubuntu Server 22.04 LTS"
4. Select "t4g.nano" (ARM) or "t3.nano" (x86)
5. Create/select key pair
6. Configure security group:
   - SSH (22) - Your IP
   - HTTP (80) - 0.0.0.0/0
   - HTTPS (443) - 0.0.0.0/0
7. Launch instance

### **2. Connect to Instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### **3. Run Deployment Script**

#### **For Ubuntu/Debian:**
```bash
# Download and run the deployment script
curl -O https://raw.githubusercontent.com/ntufar/greek-news-analyzer/main/aws-deploy.sh
chmod +x aws-deploy.sh
./aws-deploy.sh
```

#### **For Amazon Linux:**
```bash
# Download and run the Amazon Linux deployment script
curl -O https://raw.githubusercontent.com/ntufar/greek-news-analyzer/main/aws-deploy-amazon-linux.sh
chmod +x aws-deploy-amazon-linux.sh
./aws-deploy-amazon-linux.sh
```

#### **Add Your API Key:**
```bash
# The script will pause and ask you to add your API key
# Edit the .env file when prompted:
nano .env
# Add: GEMINI_API_KEY=your_actual_api_key_here
# Save and exit (Ctrl+X, Y, Enter)
```

### **4. Verify Deployment**
```bash
# Check if service is running
sudo systemctl status greek-news-analyzer

# Check logs
sudo journalctl -u greek-news-analyzer -f

# Test the application
curl http://localhost:5000
```

## 💰 **Cost Breakdown**

| Component | Monthly Cost |
|-----------|-------------|
| **t4g.nano Instance** | $3.04 |
| **8 GB EBS Storage** | $0.80 |
| **Data Transfer** | $0.00-2.00 |
| **Total** | **~$4-6/month** |

## 🔧 **Additional Configurations**

### **SSL Certificate (Free)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### **Custom Domain**
1. Point your domain to EC2 public IP
2. Update Nginx configuration
3. Get SSL certificate

### **Monitoring**
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Check system resources
htop
df -h
free -h
```

## 🛠️ **Management Commands**

```bash
# Restart application
sudo systemctl restart greek-news-analyzer

# View logs
sudo journalctl -u greek-news-analyzer -f

# Update application (Manual)
cd /var/www/greek-news-analyzer
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart greek-news-analyzer

# Check Nginx status
sudo systemctl status nginx
sudo nginx -t
```

## 🔄 **Application Updates**

### **Automatic Update (Recommended)**
```bash
# Download and run the update script
curl -O https://raw.githubusercontent.com/ntufar/greek-news-analyzer/main/aws-update.sh
chmod +x aws-update.sh

# Update with existing API key (keeps current configuration)
./aws-update.sh

# OR update with new API key
./aws-update.sh your_new_gemini_api_key_here
```

### **What the Update Script Does**
- ✅ **Pulls latest code** from GitHub repository
- ✅ **Updates dependencies** including new PWA features
- ✅ **Generates PWA icons** automatically
- ✅ **Updates Nginx configuration** with PWA headers
- ✅ **Backs up existing configuration** (API keys, settings)
- ✅ **Restarts services** with zero downtime
- ✅ **Tests deployment** and shows status

### **New Features After Update**
- 📱 **Progressive Web App (PWA)** - Install on mobile devices
- 🔗 **Deep Linking** - Handle news URLs directly
- 📤 **Share Target** - Receive shared URLs from other apps
- ⚡ **Caching System** - Faster repeated analyses
- 🚦 **Rate Limiting** - Prevents API abuse
- 📊 **Health Monitoring** - `/health` and `/status` endpoints
- 🔒 **Enhanced Security** - Better headers and validation

### **Manual Update (Alternative)**
```bash
# Stop the service
sudo systemctl stop greek-news-analyzer

# Navigate to app directory
cd /var/www/greek-news-analyzer

# Pull latest changes
git fetch origin
git reset --hard origin/main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Generate PWA icons (if needed)
python3 generate_icons.py

# Restart service
sudo systemctl start greek-news-analyzer
sudo systemctl restart nginx
```

### **Verify Update**
```bash
# Check service status
sudo systemctl status greek-news-analyzer

# Test PWA features
curl http://your-server-ip/health
curl http://your-server-ip/status

# Check if PWA manifest is accessible
curl http://your-server-ip/static/manifest.json
```

## 🔒 **Security Considerations**

1. **API Keys:** Never commit API keys to Git
2. **Environment Variables:** Store sensitive data in .env files
3. **Firewall:** Only open necessary ports
4. **SSH Key:** Use key-based authentication
5. **Updates:** Regular system updates
6. **Monitoring:** Set up CloudWatch alarms
7. **Backups:** Regular EBS snapshots

### **API Key Security**
- ✅ **Never commit** API keys to Git
- ✅ **Use .env files** for local development
- ✅ **Set environment variables** on the server
- ✅ **Rotate keys** if compromised
- ✅ **Use IAM roles** for AWS services when possible

## 📊 **Performance Optimization**

1. **Gunicorn Workers:** 2 workers (optimal for 512MB RAM)
2. **Nginx Caching:** Enable static file caching
3. **Database:** Use RDS if needed (separate cost)
4. **CDN:** CloudFront for static assets

## 🚨 **Troubleshooting**

### **Service Won't Start**
```bash
sudo journalctl -u greek-news-analyzer -n 50
```

### **Out of Memory**
```bash
# Check memory usage
free -h
# Reduce Gunicorn workers to 1
```

### **Port Already in Use**
```bash
sudo netstat -tlnp | grep :5000
sudo kill -9 <PID>
```

### **PWA Not Working**
```bash
# Check if manifest is accessible
curl -I http://your-server-ip/static/manifest.json

# Check if icons exist
ls -la /var/www/greek-news-analyzer/static/icons/

# Regenerate icons if missing
cd /var/www/greek-news-analyzer
python3 generate_icons.py

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

### **Service Worker Issues**
```bash
# Check if service worker is accessible
curl http://your-server-ip/static/sw.js

# Clear browser cache and try again
# Or check browser developer tools for errors
```

## 📱 **PWA Testing**

### **Mobile Installation**
1. **Open your app** in mobile browser
2. **Look for install prompt** or install button
3. **Add to home screen** when prompted
4. **Test standalone mode** - app should open like native app

### **URL Handling Test**
```bash
# Test deep linking
curl "http://your-server-ip/?url=https://kathimerini.gr/some-article"

# Test share target (from mobile browser)
# Share a news URL from another app to your analyzer
```

### **PWA Validation**
- **Lighthouse Audit:** Use Chrome DevTools → Lighthouse
- **Manifest Test:** Check `/static/manifest.json` is accessible
- **Service Worker:** Check `/static/sw.js` is accessible
- **Icons:** Verify all icon sizes are generated

## 🔄 **Scaling Options**

- **Vertical:** Upgrade to t3.micro (1GB RAM) - $8.47/month
- **Horizontal:** Add more instances behind load balancer
- **Database:** Move to RDS for better performance
- **Caching:** Add Redis for session storage
