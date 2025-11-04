
from PySide6.QtCore import Qt
import settings


class MovementHandler:
    def __init__(self):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.v = settings.Settings.MoveSpeed

    def getVelocity(self) -> tuple[int, int]:
        """
        Returns the velocity vector based on the current key states.
        If both keys in a direction are pressed, they cancel each other out.
        """
        vy = 0
        vx = 0
        if self.w ^ self.s:
            vy = -self.v if self.w else self.v
        if self.a ^ self.d:
            vx = -self.v if self.a else self.v
        return vx, vy

    def is_moving(self) -> bool:
        """
        Returns True if either vertical or horizontal movement is occurring.
        """
        return (self.w ^ self.s) or (self.a ^ self.d)

    def get_animation_direction(self) -> str | None:
        """
        Unlike `getVelocity` where the movement can be diagonal, there's no diagonal
        animation. So we prioritize vertical movement over horizontal movement.
        """
        if self.w ^ self.s:
            return "up" if self.w else "down"
        elif self.a ^ self.d:
            return "left" if self.a else "right"
        return None

    # --- @! event recorders -------------------------------------------------------------

    def recordKeyPress(self, event):
        key = event.key()
        match key:
            case Qt.Key.Key_W:
                self.w = True
            case Qt.Key.Key_A:
                self.a = True
            case Qt.Key.Key_S:
                self.s = True
            case Qt.Key.Key_D:
                self.d = True

    def recordKeyRelease(self, event):
        key = event.key()
        match key:
            case Qt.Key.Key_W:
                self.w = False
            case Qt.Key.Key_A:
                self.a = False
            case Qt.Key.Key_S:
                self.s = False
            case Qt.Key.Key_D:
                self.d = False

    def recordMouseLeave(self):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
