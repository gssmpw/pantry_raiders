from urllib import response

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import requests

# --- Screens ---
# Each Screen class maps to a matching <ScreenName> rule in the .kv file.
# You generally keep logic here and layout in .kv

class HomeScreen(Screen):
    def on_enter(self):
        # Called automatically when this screen becomes active
        print("Home screen entered")

    def go_to_pantry(self):
        # Navigate to another screen via the ScreenManager
        self.manager.current = "pantry"

    def go_to_list(self):
        self.manager.current = "list"

    def go_to_scanOptions(self):
        self.manager.current = "scanOptions"


class PantryScreen(Screen):
    def on_enter(self):
        print("Pantry screen entered")
        self.load_pantry()

    def go_back(self):
        self.manager.current = "home"

    def on_button_press(self):
        self.ids.result_label.text = "Sending request to backend..."

        try:
            files = {"file": ("image.jpg", b"fakeimage")}

            response = requests.post("http://127.0.0.1:8000/scan", files=files)

            if response.status_code == 200:
                data = response.json()

                # Show what backend detected
                detected = ", ".join(data["items_detected"])
                self.ids.result_label.text = f"Detected: {detected}"

                # Load pantry after short delay
                self.load_pantry()

            else:
                self.ids.result_label.text = "Error calling backend"

        except Exception as e:
            self.ids.result_label.text = f"Error: {str(e)}"

    def load_pantry(self):
        response = requests.get("http://127.0.0.1:8000/pantry")

        if response.status_code == 200:
            items = response.json()

            if not items:
                self.ids.result_label.text = "Pantry is empty"
                return

            text = "Pantry:\n"
            text += "\n".join([f"{i['name']} x{i['quantity']}" for i in items])

            self.ids.result_label.text = text


class ListScreen(Screen):
    def on_enter(self):
        print("List screen entered")
        self.ids.result_label.text = "Grocery List"

    def go_back(self):
        self.manager.current = "home"

    def on_button_press(self):
        # Update a label defined in the .kv file using its id
        self.ids.result_label.text = "Generating List..."


class ScanOptionsScreen(Screen):
    def on_enter(self):
        print("ScanOptions screen entered")

    def go_back(self):
        self.manager.current = "home"

    def picture_button_press(self):
        self.manager.current = "scanPicture"
    
    def receipt_button_press(self):
        self.manager.current = "scanReceipt"


class ScanPictureScreen(Screen):
    def on_enter(self):
        print("ScanPicture screen entered")
        self.ids.result_label.text = "Take a Picture of Your Pantry"

    def go_back(self):
        self.manager.current = "scanOptions"

    def on_button_press(self):
        self.ids.result_label.text = "Sending request to backend..."

        try:
            files = {"file": ("image.jpg", b"fakeimage")}

            response = requests.post("http://127.0.0.1:8000/scan", files=files)

            if response.status_code == 200:
                data = response.json()

                # Show what backend detected
                detected = ", ".join(data["items_detected"])
                self.ids.result_label.text = f"Detected: {detected}"

                # Load pantry after short delay
                self.manager.current = "pantry"

            else:
                self.ids.result_label.text = "Scan Failed"

        except Exception as e:
            self.ids.result_label.text = f"Error: {str(e)}"


class ScanReceiptScreen(Screen):
    def on_enter(self):
        print("ScanReceipt screen entered")
        self.ids.result_label.text = "Take a Picture of Your Receipt"

    def go_back(self):
        self.manager.current = "scanOptions"

    def on_button_press(self):
        # Update a label defined in the .kv file using its id
        self.ids.result_label.text = "Receipt Scan In Progress..."


# --- Root Widget ---
# This is what build() returns. It holds the ScreenManager.

class RootWidget(BoxLayout):
    pass  # Layout and children are fully defined in .kv


# --- App Class --- #
class PantryRaidersApp(App):
    def build(self):
        print("App is building...")
        return RootWidget()


if __name__ == "__main__":
    PantryRaidersApp().run()