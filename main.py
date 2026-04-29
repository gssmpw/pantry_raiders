from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import requests
import cv2
from ultralytics import YOLO
from kivy.graphics.texture import Texture


API_URL = "http://127.0.0.1:8000"


class LoginScreen(Screen):

    def validate_login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        error_label = self.ids.error_label

        if not username or not password:
            error_label.text = "Please fill in all fields."
            return

        if username == "admin" and password == "1234":
            error_label.text = ""
            self.manager.current = "home"
        else:
            error_label.text = "Invalid username or password."

    def toggle_password(self):
        field = self.ids.password_input
        btn = self.ids.toggle_btn

        if field.password:
            field.password = False
            btn.text = "Hide"
        else:
            field.password = True
            btn.text = "Show"


class HomeScreen(Screen):
    def on_enter(self):
        print("Home screen entered")

    def go_to_pantry(self):
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
        self.load_pantry()

    def load_pantry(self):
        self.ids.result_label.text = "Loading pantry..."

        try:
            response = requests.get(f"{API_URL}/pantry")

            if response.status_code == 200:
                items = response.json()

                if not items:
                    self.ids.result_label.text = "Pantry is empty"
                    return

                text = "Pantry Inventory\n\n"

                for item in items:
                    text += f"{item['name']} x{item['quantity']}\n"

                self.ids.result_label.text = text

            else:
                self.ids.result_label.text = "Server error loading pantry"

        except Exception as e:
            self.ids.result_label.text = "Could not connect to server"
            print(f"Backend error: {e}")


class ListScreen(Screen):
    def on_enter(self):
        print("List screen entered")
        self.load_grocery_list()

    def go_back(self):
        self.manager.current = "home"

    def on_button_press(self):
        self.load_grocery_list()

    def load_grocery_list(self):
        self.ids.result_label.text = "Generating grocery list..."

        try:
            response = requests.get(f"{API_URL}/grocery-list")

            if response.status_code == 200:
                items = response.json()

                if not items:
                    self.ids.result_label.text = "No grocery items needed"
                    return

                text = "Grocery List\n\n"

                for item in items:
                    text += f"{item['name']} - Buy {item['suggested_quantity']}\n"

                self.ids.result_label.text = text

            else:
                self.ids.result_label.text = "Server error loading grocery list"

        except Exception as e:
            self.ids.result_label.text = "Could not connect to server"
            print(f"Backend error: {e}")


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
        self.model = YOLO(r"C:/Users/gsmit/Documents/pantry_raiders/runs/detect/grocery_yolov82/weights/best.pt")
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30)

    def on_leave(self):
        Clock.unschedule(self.update)
        if hasattr(self, 'capture'):
            self.capture.release()

    def go_back(self):
        self.manager.current = "scanOptions"

    def update(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        results = self.model(frame, conf=0.5, verbose=False)
        annotated = results[0].plot()

        buf = cv2.flip(annotated, 0).tobytes()
        texture = Texture.create(size=(annotated.shape[1], annotated.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.camera_feed.texture = texture

    def on_button_press(self):
        ret, frame = self.capture.read()
        if not ret:
            return

        results = self.model(frame, conf=0.5, verbose=False)
        detected_names = [
            self.model.names[int(box.cls)]
            for box in results[0].boxes
        ]

        if not detected_names:
            self.ids.result_label.text = "Nothing detected"
            return

        try:
            response = requests.post(f"{API_URL}/scan/pantry", json={"items_detected": detected_names})
            if response.status_code == 200:
                self.ids.result_label.text = f"Detected:\n{', '.join(detected_names)}"
                Clock.schedule_once(
                    lambda dt: setattr(self.manager, "current", "pantry"), 1.5
                )
            else:
                self.ids.result_label.text = "Scan failed"
        except Exception as e:
            self.ids.result_label.text = f"Error: {str(e)}"


class ScanReceiptScreen(Screen):
    def on_enter(self):
        print("ScanReceipt screen entered")
        self.ids.result_label.text = "Take a Picture of Your Receipt"

    def go_back(self):
        self.manager.current = "scanOptions"

    def on_button_press(self):
        self.ids.result_label.text = "Scanning receipt..."

        try:
            files = {"file": ("receipt.jpg", b"fakereceipt")}

            response = requests.post(f"{API_URL}/scan/receipt", files=files)

            if response.status_code == 200:
                data = response.json()

                detected = ", ".join(data["items_detected"])
                self.ids.result_label.text = f"Receipt Items:\n{detected}"

                Clock.schedule_once(
                    lambda dt: setattr(self.manager, "current", "pantry"),
                    1.5
                )

            else:
                self.ids.result_label.text = "Receipt scan failed"

        except Exception as e:
            self.ids.result_label.text = f"Error: {str(e)}"


class RootWidget(BoxLayout):
    pass


class PantryRaidersApp(App):
    kv_file = "PantryRaiders.kv"

    def build(self):
        print("App is building...")
        return RootWidget()


if __name__ == "__main__":
    PantryRaidersApp().run()