from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen


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


class PantryScreen(Screen):
    def on_enter(self):
        print("Pantry screen entered")
        self.ids.result_label.text = "Pantry Inventory"

    def go_back(self):
        self.manager.current = "home"

    def on_button_press(self):
        # Update a label defined in the .kv file using its id
        self.ids.result_label.text = "Generating Inventory..."


class ListScreen(Screen):
    def on_enter(self):
        print("List screen entered")
        self.ids.result_label.text = "Grocery List"

    def go_back(self):
        self.manager.current = "home"

    def on_button_press(self):
        # Update a label defined in the .kv file using its id
        self.ids.result_label.text = "Generating List..."



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