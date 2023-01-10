# Disable the WiFi to prevent connection after restarting.
# Shutdown the computer/device
# Remove the ethernet cable
# Power on the computer/device
# Open a terminal and run the following commands:
echo "on_acquisition_ping_failure = 'ignore'" | sudo tee /opt/ont/minknow/conf/installation_overrides.toml

# Restart the MinKNOW service by running the following commands:
sudo systemctl daemon-reload
sudo systemctl enable minknow
sudo systemctl start minknow

# Shutdown the computer/device
# Power on the computer/device
