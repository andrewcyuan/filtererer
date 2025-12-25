# Set Web Proxy (HTTP)
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8080
# Set Secure Web Proxy (HTTPS)
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8080

mitmdump -s traffic_control.py

