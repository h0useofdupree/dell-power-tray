import sys, smbios_interface, os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize smbios interface and get the current thermal and battery modes
        self.smbios = smbios_interface.smbiosInterface()
        self.thermal_mode = self.smbios.get_thermal()
        self.battery_mode = self.smbios.get_battery()
        
        self.setToolTip("Dell Power Tray")

        # Create the menu
        self.menu = QMenu()

        # Add the main entries
        thermal_entry = self.menu.addMenu(f"Current Thermal Mode: {self.capitalize(self.replace(self.thermal_mode, ['_', '-'], ' '))}")
        thermal_entry.setIcon(QIcon.fromTheme("temperature-normal"))
        battery_entry = self.menu.addMenu(f"Current Battery Mode: {self.capitalize(self.replace(self.battery_mode, ['_', '-'], ' '))}")
        battery_entry.setIcon(QIcon.fromTheme("battery-normal"))

        # Add the sub-entries for Thermal
        for i in self.smbios.thermal_modes:
            sub_entry = QAction(self.format(i), self) # Set the text to the mode name
            sub_entry.triggered.connect(lambda _, i=i: self.set_thermal(i)) # Set the action to set the thermal mode
            thermal_entry.addAction(sub_entry) # Add the sub-entry to the menu

        # Add the sub-entries for Battery
        for i in self.smbios.battery_modes:
            sub_entry = QAction(self.format(i), self) # Set the text to the mode name
            sub_entry.triggered.connect(lambda _, i=i: self.set_battery(i)) # Set the action to set the battery mode
            battery_entry.addAction(sub_entry) # Add the sub-entry to the menu

        # Add the exit button
        exit_button = QAction("Exit", self)
        exit_button.setIcon(QIcon.fromTheme("application-exit"))
        exit_button.triggered.connect(QApplication.quit)
        self.menu.addAction(exit_button)

        # Set the menu
        self.setContextMenu(self.menu)

    def set_thermal(self, mode):
        print(f"Set Thermal {mode}")
        self.smbios.set_thermal(mode)
        self.thermal_mode = self.smbios.get_thermal()
        self.menu.actions()[0].setText(f"Current Thermal Mode: {self.format(self.thermal_mode)}")
        self.icon_refresh()

    def set_battery(self, mode):
        print(f"Set Battery {mode}")
        self.smbios.set_battery(mode)
        self.battery_mode = self.smbios.get_battery()
        self.menu.actions()[1].setText(f"Current Battery Mode: {self.format(self.battery_mode)}")

    def icon_refresh(self):
        # Set dynamic icons if the system is running KDE
        if (self.is_kde()):
            if (self.thermal_mode == "balanced"):
                self.setIcon(QIcon.fromTheme("face-smile"))
            elif (self.thermal_mode == "cool-bottom"):
                self.setIcon(QIcon.fromTheme("face-cool"))
            elif (self.thermal_mode == "quiet"):
                self.setIcon(QIcon.fromTheme("face-ninja"))
            elif (self.thermal_mode == "performance"):
                self.setIcon(QIcon.fromTheme("face-devilish"))

    # Helper method to replace mulitple characters in a string
    def replace(self, string, chars, replacement):
        for i in chars:
            string = string.replace(i, replacement)
        return string

    # Helper method to capitalize all words in a string
    def capitalize(self, string):
        return ' '.join([i.capitalize() for i in string.split()])

    # Helper method to format strings for the menu
    def format(self, string):
        # Replace all underscores and dashes with spaces
        string = self.capitalize(self.replace(string, ['_', '-'], ' '))
        # Make all words containing 2 or less characters uppercase
        return ' '.join([i.upper() if len(i) <= 2 else i for i in string.split()])

    # Function to detect if the system is running KDE or not
    def is_kde(self):
        return os.environ.get("XDG_CURRENT_DESKTOP") == "KDE"


# Method to install to ~/.local/share/applications
def install():
    # Get the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # Get python path
    python_path = os.popen("which python3").read().strip()

    # Create the .desktop file
    desktop_file = f"""[Desktop Entry]
    Name=Dell Power Tray
    Comment=Power management for Dell laptops
    Exec={python_path} {current_dir}/main.py
    Icon={current_dir}/icon.png
    Terminal=false
    Type=Application
    Categories=Utility;"""

    # Write the .desktop file to the current users .local/share/applications directory
    home = os.path.expanduser("~")
    with open(f"{home}/.local/share/applications/dell-power-tray.desktop", "w") as f:
        f.write(desktop_file)

# Uninstall from ~/.local/share/applications
def uninstall():
    # remove file
    home = os.path.expanduser("~")
    os.remove(f"{home}/.local/share/applications/dell-power-tray.desktop")


# Main method
if __name__ == "__main__":
    # Check for install/uninstall flags
    for i in sys.argv:
        if (i == "--install"):
            install()
            print("Installed. The application should now appear in your application menu.")
            sys.exit(0)
        elif (i == "--uninstall"):
            uninstall()
            print("Uninstalled. The application should no longer appear in your application menu.")
            sys.exit(0)

    app = QApplication(sys.argv)

    # Set initial icon
    icon = QIcon.fromTheme(f"{os.path.dirname(os.path.realpath(__file__))}/icon.png")

    # Create the system tray icon
    tray_icon = SystemTrayIcon()
    tray_icon.setIcon(icon)
    tray_icon.setVisible(True)
    if (tray_icon.is_kde()):
        tray_icon.icon_refresh()

    # Run the application
    sys.exit(app.exec_())
