
import sys
import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import Qt, QTimer, QRect, QUrl
from PySide6.QtGui import QIcon, QAction
from PySide6.QtMultimedia import QSoundEffect

import settings
import sprite_manager
from movement_handler import MovementHandler
from settings import State


class GremlinWindow(QWidget):

    def __init__(self):
        super().__init__()

        # --- @! Window Setup ------------------------------------------------------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(
            settings.Settings.FrameWidth + 215,
            settings.Settings.FrameHeight + 30
        )

        # --- @! Main Sprite Display -----------------------------------------------------
        self.sprite_label = QLabel(self)
        self.sprite_label.setGeometry(
            105, 5, settings.Settings.FrameWidth, settings.Settings.FrameHeight)
        self.sprite_label.setScaledContents(True)

        # --- @! Hotspots ----------------------------------------------------------------
        self.left_hotspot = QWidget(self)
        self.left_hotspot.setGeometry(110, 95, 60, 85)
        self.left_hotspot.mousePressEvent = self.left_hotspot_click

        self.right_hotspot = QWidget(self)
        self.right_hotspot.setGeometry(280, 95, 60, 85)
        self.right_hotspot.mousePressEvent = self.right_hotspot_click

        self.top_hotspot = QWidget(self)
        self.top_hotspot.setGeometry(160, 0, 135, 50)
        self.top_hotspot.mousePressEvent = self.top_hotspot_click

        # --- @! Sound Player ------------------------------------------------------------
        self.sound_player = QSoundEffect(self)
        self.sound_player.setVolume(0.8)

        # --- @! Timers ------------------------------------------------------------------
        self.master_timer = QTimer(self)
        self.master_timer.timeout.connect(self.animation_tick)

        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.idle_timer_tick)

        self.close_timer = None

        # --- @! State Management --------------------------------------------------------
        self.movement_handler = MovementHandler()
        self.current_state = State.INTRO
        self.drag_pos = None

        # --- @! Start -------------------------------------------------------------------
        self.setup_tray_icon()
        self.play_sound("intro.wav")
        self.master_timer.start(1000 // settings.Settings.FrameRate)
        self.idle_timer.start(120 * 1000)

    # --- @! State Machine Core -------------------------------------------------------

    def set_state(self, new_state: State):
        """ Handles playing entry sounds and resetting animation frames. """
        if self.current_state == new_state:
            return

        # handles sound effects on state transitions
        if new_state == State.DRAGGING:
            self.play_sound("grab.wav")
        elif new_state == State.WALKING and self.current_state != State.WALKING:
            self.play_sound("run.wav")
        elif new_state == State.CLICK:
            self.play_sound("mambo.wav")
        elif new_state == State.PAT:
            self.play_sound("grab.wav")

        self.current_state = new_state
        self.reset_current_frames(new_state)

    def reset_current_frames(self, state: State):
        """ Resets the frame counter for the new state. """
        c = settings.CurrentFrames
        match state:
            case State.INTRO:
                c.Intro = 0
            case State.IDLE:
                c.Idle = 0
            case State.HOVER:
                c.Hover = 0
            case State.WALKING:
                c.WalkUp = c.WalkDown = c.WalkLeft = c.WalkRight = 0
            case State.DRAGGING:
                c.Grab = 0
            case State.CLICK:
                c.Click = 0
            case State.PAT:
                c.Pat = 0
            case State.SLEEPING:
                c.Sleep = 0

    # --- @! Animations ------------------------------------------------------------------

    def play_animation(self, sheet, current_frame, frame_count):
        if sheet is None or frame_count == 0:
            return current_frame

        s = settings.Settings
        x = (current_frame % s.SpriteColumn) * s.FrameWidth
        y = (current_frame // s.SpriteColumn) * s.FrameHeight

        # check bounds
        if x + s.FrameWidth > sheet.width() or y + s.FrameHeight > sheet.height():
            print("Warning: Animation frame out of bounds.")
            return (current_frame + 1) % frame_count

        # create the cropped pixmap
        crop_rect = QRect(x, y, s.FrameWidth, s.FrameHeight)
        cropped_pixmap = sheet.copy(crop_rect)
        self.sprite_label.setPixmap(cropped_pixmap)

        return (current_frame + 1) % frame_count

    def animation_tick(self):
        """ Plays the animation for the current state. """
        c = settings.CurrentFrames
        f = settings.FrameCounts

        match self.current_state:
            case State.INTRO:
                c.Intro = self.play_animation(
                    sprite_manager.get("intro"), c.Intro, f.Intro)
                if c.Intro == 0:
                    self.set_state(State.IDLE)

            case State.IDLE:
                c.Idle = self.play_animation(
                    sprite_manager.get("idle"), c.Idle, f.Idle)

            case State.HOVER:
                c.Hover = self.play_animation(
                    sprite_manager.get("hover"), c.Hover, f.Hover)

            case State.WALKING:
                self.handle_walking_animation_and_movement()

            case State.DRAGGING:
                c.Grab = self.play_animation(
                    sprite_manager.get("grab"), c.Grab, f.Grab)

            case State.PAT:
                c.Pat = self.play_animation(
                    sprite_manager.get("pat"), c.Pat, f.Pat)
                if c.Pat == 0:
                    # transition to Hover or Idle when "pat" animation finishes
                    self.set_state(
                        State.HOVER if self.underMouse() else State.IDLE)

            case State.CLICK:
                c.Click = self.play_animation(
                    sprite_manager.get("click"), c.Click, f.Click)
                if c.Click == 0:
                    # transition to Hover or Idle when "click" animation finishes
                    self.set_state(
                        State.HOVER if self.underMouse() else State.IDLE)

            case State.SLEEPING:
                c.Sleep = self.play_animation(
                    sprite_manager.get("sleep"), c.Sleep, f.Sleep)

            case State.OUTRO:
                # this state is handled by outro_tick, but we stop master_timer
                # so this case is just a failsafe.
                pass

    def handle_walking_animation_and_movement(self):
        """ Helper function to keep animation_tick clean. """
        c = settings.CurrentFrames
        f = settings.FrameCounts

        direction = self.movement_handler.get_animation_direction()

        if direction == "left":
            c.WalkLeft = self.play_animation(
                sprite_manager.get("left"), c.WalkLeft, f.Left)
        elif direction == "right":
            c.WalkRight = self.play_animation(
                sprite_manager.get("right"), c.WalkRight, f.Right)
        elif direction == "up":
            c.WalkUp = self.play_animation(
                sprite_manager.get("backward"), c.WalkUp, f.Up)
        elif direction == "down":
            c.WalkDown = self.play_animation(
                sprite_manager.get("forward"), c.WalkDown, f.Down)

        # apply the new position to the window
        dx, dy = self.movement_handler.getVelocity()
        if dx != 0 or dy != 0:
            self.move(self.pos().x() + dx, self.pos().y() + dy)

    def play_sound(self, file_name, delay_seconds=0):
        """ Plays a sound, respecting the LastPlayed delay. """
        path = os.path.join(
            settings.BASE_DIR, "Sounds", settings.Settings.StartingChar, file_name)
        if not os.path.exists(path):
            return

        if delay_seconds > 0:
            last_time = settings.Settings.LastPlayed.get(file_name)
            if last_time:
                if (datetime.datetime.now() - last_time).total_seconds() < delay_seconds:
                    return

        try:
            self.sound_player.setSource(QUrl.fromLocalFile(path))
            self.sound_player.play()
            settings.Settings.LastPlayed[file_name] = datetime.datetime.now()
        except Exception as e:
            print(f"Sound error: {e}")

    # --- @! System Tray and App Lifecycle ---------------------------------------------------------

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)

        icon_path = os.path.join(settings.BASE_DIR, "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(settings.BASE_DIR, "icon.png")

        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("applications-games"))

        self.tray_icon.setToolTip("Gremlin")

        menu = QMenu()
        menu.addSeparator()

        reappear_action = QAction("Reappear", self)
        reappear_action.triggered.connect(self.reset_app)
        menu.addAction(reappear_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close_app)
        menu.addAction(close_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def reset_app(self):
        self.tray_icon.hide()
        QApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def close_app(self):
        self.master_timer.stop()
        self.idle_timer.stop()
        self.tray_icon.hide()

        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.outro_tick)
        self.close_timer.start(1000 // settings.Settings.FrameRate)

    def outro_tick(self):
        s = settings
        s.CurrentFrames.Outro = self.play_animation(
            sprite_manager.get("outro"),
            s.CurrentFrames.Outro,
            s.FrameCounts.Outro
        )

        if s.CurrentFrames.Outro == 0:
            self.close_timer.stop()
            QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.close_app()

    # --- @! Event Handlers (Mouse) ------------------------------------------------------

    def reset_idle_timer(self):
        """ Resets the idle timer and wakes the gremlin up if sleeping. """
        self.idle_timer.start(120 * 1000)
        if self.current_state == State.SLEEPING:
            self.set_state(State.IDLE)

    def idle_timer_tick(self):
        """ When timer fires, go to sleep. """
        if self.current_state in [State.IDLE, State.HOVER]:
            self.set_state(State.SLEEPING)

    def mousePressEvent(self, event):
        self.reset_idle_timer()
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_state not in [State.DRAGGING, State.PAT, State.CLICK]:
                self.set_state(State.DRAGGING)
                self.drag_pos = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            if self.current_state not in [State.DRAGGING, State.PAT, State.CLICK]:
                self.set_state(State.CLICK)

    def mouseMoveEvent(self, event):
        if (self.current_state == State.DRAGGING and
                event.buttons() == Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_state == State.DRAGGING:
                # transition to Hover or Idle when dropped
                self.set_state(State.HOVER if self.underMouse()
                               else State.IDLE)
                self.play_sound("run.wav")

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        # don't allow walking while in these blocking states
        if self.current_state in [State.DRAGGING, State.PAT, State.CLICK, State.SLEEPING]:
            return

        self.movement_handler.recordKeyPress(event)

        if self.movement_handler.is_moving():
            self.set_state(State.WALKING)
            self.reset_idle_timer()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        self.movement_handler.recordKeyRelease(event)

        # if we were walking and are no longer moving...
        if self.current_state == State.WALKING and not self.movement_handler.is_moving():
            # ...transition to hover or idle.
            self.set_state(State.HOVER if self.underMouse() else State.IDLE)

    def enterEvent(self, event):
        self.setFocus()
        self.reset_idle_timer()
        if self.current_state == State.IDLE:
            self.set_state(State.HOVER)

        if self.current_state not in [State.WALKING, State.SLEEPING, State.CLICK, State.DRAGGING]:
            self.play_sound("hover.wav", 3)

    def leaveEvent(self, event):
        self.clearFocus()
        self.movement_handler.recordMouseLeave()    # stop all movement

        # if we were hovering or walking, transition to idle.
        if self.current_state in [State.HOVER, State.WALKING]:
            self.set_state(State.IDLE)

    # --- @! Hotspot Click Handlers ------------------------------------------------------

    def top_hotspot_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_state not in [State.DRAGGING, State.CLICK, State.SLEEPING]:
                self.reset_idle_timer()
                self.set_state(State.PAT)

    def left_hotspot_click(self, event):
        pass  # firing removed

    def right_hotspot_click(self, event):
        pass  # firing removed
