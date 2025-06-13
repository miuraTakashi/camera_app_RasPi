#!/bin/bash

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 関数: 色付きのメッセージを表示
print_message() {
    echo -e "${2}${1}${NC}"
}

# 関数: エラーメッセージを表示して終了
error_exit() {
    print_message "$1" "$RED"
    exit 1
}

# 関数: 成功メッセージを表示
success_message() {
    print_message "$1" "$GREEN"
}

# 関数: 警告メッセージを表示
warning_message() {
    print_message "$1" "$YELLOW"
}

# 関数: Python依存関係のインストール
install_python_dependencies() {
    print_message "Installing Python dependencies..." "$YELLOW"
    
    # システムパッケージを使用してPython依存関係をインストール
    print_message "Installing system Python packages..." "$YELLOW"
    sudo apt-get install -y python3-numpy python3-picamera python3-picamera2 || warning_message "Some system packages may not be available"
    
    # pipをアップグレード
    python3 -m pip install --upgrade pip || error_exit "Failed to upgrade pip"
    
    # 基本的な依存関係を個別にインストール
    print_message "Installing basic dependencies..." "$YELLOW"
    python3 -m pip install --no-cache-dir opencv-python || error_exit "Failed to install opencv-python"
    
    # その他の軽量な依存関係をインストール
    print_message "Installing other dependencies..." "$YELLOW"
    python3 -m pip install --no-cache-dir Pillow || warning_message "Failed to install Pillow, continuing..."
    
    success_message "Python dependencies installed successfully"
}

# 関数: 自動起動の設定
setup_autostart() {
    local username=$1
    local autostart=$2

    if [ "$autostart" = "y" ] || [ "$autostart" = "Y" ]; then
        print_message "Setting up automatic startup..." "$YELLOW"
        
        # systemdサービスの設定
        sudo tee /etc/systemd/system/camera-app.service > /dev/null << EOL
[Unit]
Description=Camera Application
After=network.target

[Service]
Type=simple
User=${username}
WorkingDirectory=/home/${username}/camera_app_RasPi
ExecStart=/usr/bin/python3 /home/${username}/camera_app_RasPi/camera_app.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

        # サービスを有効化して開始
        sudo systemctl daemon-reload || error_exit "Failed to reload systemd"
        sudo systemctl enable camera-app || error_exit "Failed to enable camera-app service"
        sudo systemctl start camera-app || error_exit "Failed to start camera-app service"
        
        success_message "Automatic startup has been configured"
    else
        warning_message "Automatic startup has been skipped"
    fi
}

# メインのインストール処理
print_message "Starting installation of Camera Application..." "$YELLOW"

# システムの更新
print_message "Updating system packages..." "$YELLOW"
sudo apt-get update || error_exit "Failed to update system packages"
sudo apt-get upgrade -y || error_exit "Failed to upgrade system packages"

# 必要なパッケージのインストール
print_message "Installing required packages..." "$YELLOW"
sudo apt-get install -y python3-pip python3-opencv python3-dev python3-setuptools python3-wheel build-essential cmake || error_exit "Failed to install required packages"

# Python依存関係のインストール
install_python_dependencies

# ユーザー名の取得
username=$(whoami)
print_message "Detected username: ${username}" "$GREEN"

# 自動起動の設定を確認
while true; do
    read -p "Do you want to set up automatic startup? (y/n): " autostart
    case $autostart in
        [Yy]* ) setup_autostart "$username" "y"; break;;
        [Nn]* ) setup_autostart "$username" "n"; break;;
        * ) print_message "Please answer y or n." "$RED";;
    esac
done

# ビデオグループへのユーザー追加
print_message "Adding user to video group..." "$YELLOW"
sudo usermod -a -G video ${username} || error_exit "Failed to add user to video group"

success_message "Installation completed successfully!"

# 使用方法の表示
print_message "\nTo start the application manually:" "$YELLOW"
echo "python3 camera_app.py"

if [ "$autostart" = "y" ] || [ "$autostart" = "Y" ]; then
    print_message "\nThe application will start automatically after reboot." "$GREEN"
    print_message "To check the status of the service:" "$YELLOW"
    echo "sudo systemctl status camera-app"
    print_message "To view the logs:" "$YELLOW"
    echo "sudo journalctl -u camera-app -f"
fi

print_message "\nPlease reboot your system to apply all changes." "$YELLOW" 