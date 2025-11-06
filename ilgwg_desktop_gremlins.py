
import sys
from PySide6.QtWidgets import QApplication

import config_manager
from gremlin import GremlinWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # please load configuration files before creating the main window
    try:
        state = (config_manager.load_master_config(sys.argv) and
                 config_manager.load_sprite_map() and
                 config_manager.load_frame_count() and
                 config_manager.load_emote_config())
        if not state:
            print("Fatal Error: Corrupted configuration. Quitting...")
            sys.exit(1)
    except Exception as e:
        print(f"Fatal Error: Could not load configuration. {e}")
        sys.exit(1)

    window = GremlinWindow()
    window.show()
    sys.exit(app.exec())
