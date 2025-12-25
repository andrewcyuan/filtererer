cleanup() {
    sudo networksetup -setsecurewebproxystate "Wi-Fi" off              
    sudo networksetup -setwebproxystate "Wi-Fi" off 

    exit 1
}

# Run cleanup when the script exits for any reason
trap cleanup EXIT SIGINT SIGTERM SIGHUP

# Set Web Proxy (HTTP)
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8080
# Set Secure Web Proxy (HTTPS)
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8080

# Run the script
mitmdump -s traffic_control.py

