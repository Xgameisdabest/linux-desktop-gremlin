
from enum import Enum, auto
import os
import datetime
from typing import Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class State(Enum):
    INTRO = auto()
    IDLE = auto()
    HOVER = auto()
    WALKING = auto()
    DRAGGING = auto()
    CLICK = auto()
    PAT = auto()
    SLEEPING = auto()
    OUTRO = auto()


class Settings:
    # Why do I use "Matikanetannhauser" instead of "Mambo", you might ask?
    # Well, my name is iluvgirlswithglasses, what do you expect about my length preferences?
    StartingChar = "Matikanetannhauser"
    SpriteColumn = 10
    FrameRate = 31
    FollowRadius = 150.0
    FrameWidth = 200
    FrameHeight = 200
    LastPlayed: Dict[str, datetime.datetime] = {}
    MoveSpeed = 5


class MouseSettings:
    # Cursor's information is restricted in wayland, so there's no much we can do here.
    LastMousePosition = None
    FollowSpeed = 5.0
    MouseX = 0.0
    MouseY = 0.0
    Speed = 10.0


class FrameCounts:
    Intro = 0
    Idle = 0
    Left = 0
    Right = 0
    Up = 0
    Down = 0
    Outro = 0
    Grab = 0
    WalkIdle = 0
    Click = 0
    Dance = 0
    Hover = 0
    Sleep = 0
    Pat = 0


class CurrentFrames:
    Intro = 0
    Idle = 0
    Outro = 0
    WalkDown = 0
    WalkUp = 0
    WalkRight = 0
    WalkLeft = 0
    Grab = 0
    WalkIdle = 0
    Click = 0
    Dance = 0
    Hover = 0
    Sleep = 0
    Pat = 0
