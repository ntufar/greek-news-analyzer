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

# Update application
cd /var/www/greek-news-analyzer
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart greek-news-analyzer

# Check Nginx status
sudo systemctl status nginx
sudo nginx -t
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

## 🔄 **Scaling Options**

- **Vertical:** Upgrade to t3.micro (1GB RAM) - $8.47/month
- **Horizontal:** Add more instances behind load balancer
- **Database:** Move to RDS for better performance
- **Caching:** Add Redis for session storage
