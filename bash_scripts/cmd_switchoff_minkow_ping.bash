# Disable the WiFi to prevent connection after restarting.
# Shutdown the computer/device
# Remove the ethernet cable
# Power on the computer/device
# Open a terminal and run the following commands:
sudo /opt/ont/minknow/bin/config_editor --filename /opt/ont/minknow/conf/sys_conf --conf system --set on_acquisition_ping_failure=ignore

# Restart the MinKNOW service by running the following commands:
sudo systemctl daemon-reload
sudo systemctl enable minknow
sudo systemctl start minknow

# Shutdown the computer/device
# Power on the computer/device
