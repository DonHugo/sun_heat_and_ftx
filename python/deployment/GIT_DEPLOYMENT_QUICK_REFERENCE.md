# Git Deployment Quick Reference

## 🚀 **Initial Setup on Raspberry Pi**

```bash
# SSH into Raspberry Pi
ssh pi@your-pi-ip-address

# Clone repository
git clone https://github.com/yourusername/sun_heat_and_ftx.git /home/pi/solar_heating
cd /home/pi/solar_heating

# Run deployment script
chmod +x python/deploy_to_pi.sh
./python/deploy_to_pi.sh
```

## 🔄 **Daily Update Workflow**

### **On Your Development Machine:**
```bash
# Make changes and test
# Commit and push
git add .
git commit -m "Description of changes"
git push origin main
```

### **On Raspberry Pi:**
```bash
# SSH into Pi
ssh pi@your-pi-ip-address

# Run update script
cd /home/pi/solar_heating
./python/update_solar_heating.sh
```

## 🔧 **System Management**

### **Check Status:**
```bash
system_switch.py status
```

### **Switch Systems:**
```bash
system_switch.py v1    # Switch to v1
system_switch.py v3    # Switch to v3
```

### **View Logs:**
```bash
system_switch.py logs      # Active system
system_switch.py logs-v1   # v1 logs
system_switch.py logs-v3   # v3 logs
```

## 🚨 **Emergency Commands**

### **Quick Rollback:**
```bash
cd /home/pi/solar_heating
git reset --hard HEAD~1
sudo systemctl restart temperature_monitoring.service
sudo systemctl restart solar_heating_v3.service
```

### **Switch to v1 Only:**
```bash
sudo systemctl stop solar_heating_v3.service
sudo systemctl start temperature_monitoring.service
```

### **Check What's Running:**
```bash
sudo systemctl status temperature_monitoring.service
sudo systemctl status solar_heating_v3.service
```

## 📊 **Monitoring**

### **Health Check:**
```bash
/home/pi/health_check.sh
```

### **MQTT Test:**
```bash
mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "test" -m "hello"
```

### **Version Check:**
```bash
cd /home/pi/solar_heating
git log --oneline -1
```

## 📋 **File Locations**

- **Project**: `/home/pi/solar_heating/`
- **v1 System**: `/usr/local/bin/temperature_monitoring.py`
- **v3 System**: `/home/pi/solar_heating/python/v3/`
- **Services**: `/etc/systemd/system/`
- **Logs**: `journalctl -u service-name`

## 🔐 **SSH Setup (Optional)**

```bash
# Generate SSH key on development machine
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy to Raspberry Pi
ssh-copy-id pi@your-pi-ip-address

# Use SSH for Git (on Pi)
cd /home/pi/solar_heating
git remote set-url origin git@github.com:yourusername/sun_heat_and_ftx.git
```

## 📞 **Troubleshooting**

### **Service Won't Start:**
```bash
sudo journalctl -u service-name -n 50
```

### **Git Issues:**
```bash
git status
git fetch origin
git pull origin main
```

### **Permission Issues:**
```bash
sudo chown -R pi:pi /home/pi/solar_heating
sudo chmod -R 755 /home/pi/solar_heating
```

---

**This quick reference covers the most common Git deployment operations for your solar heating system.**
