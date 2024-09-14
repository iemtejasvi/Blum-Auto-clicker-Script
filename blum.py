import os
import asyncio
import random
from itertools import product
from typing import Tuple, Any

import sys
import keyboard
import pygetwindow as gw
import pyautogui
from pynput.mouse import Button, Controller
from loguru import logger
from dataclasses import dataclass

# Static content
AUTOCLICKER_TEXT = """
██████╗░██╗░░░░░██╗░░░██╗███╗░░░███╗
██╔══██╗██║░░░░░██║░░░██║████╗░████║
██████╦╝██║░░░░░██║░░░██║██╔████╔██║
██╔══██╗██║░░░░░██║░░░██║██║╚██╔╝██║
██████╦╝███████╗╚██████╔╝██║░╚═╝░██║
╚═════╝░╚══════╝░╚═════╝░╚═╝░░░░░╚═╝

Blum Script by Tejasvi
"""

CREDITS = "\033[34mReach me on Telegram: https://t.me/silverda2\033[0m"
WINDOW_NOT_FOUND = "Oops! Blum's AutoClicker window is playing hide-and-seek. Maybe check behind the couch?"

# Utilities Class
@dataclass
class Utilities:

    @staticmethod
    def get_rect(window) -> Tuple[int, int, int, int]:
        """
        Get the rectangle coordinates of the given window.
        :param window: The window object
        :return: A tuple containing the coordinates (left, top, width, height)
        """
        return window.left, window.top, window.width, window.height

    @staticmethod
    def capture_screenshot(rect: Tuple[int, int, int, int]) -> Any:
        """
        Capture a screenshot of the specified region.
        :param rect: A tuple containing the region coordinates (left, top, width, height)
        :return: A screenshot image of the specified region
        """
        return pyautogui.screenshot(region=rect)


# BlumClicker Class
class BlumClicker:
    def __init__(self):
        self.mouse: Controller = Controller()
        self.utils = Utilities()
        self.running: bool = False
        self.window_options: str | None = None

    async def click(self, x: int, y: int) -> None:
        """
        Perform a click at the given (x, y) position with a slight offset.
        """
        self.mouse.position = (x, y + random.randint(1, 3))
        self.mouse.press(Button.left)
        self.mouse.release(Button.left)

    async def handle_input(self) -> bool:
        """
        Handles input, toggles start/stop of the clicker when 's' is pressed.
        """
        if keyboard.is_pressed("s"):
            self.running = not self.running
            if self.running:
                logger.info("Started the clicker. Press 's' to stop.")
            else:
                logger.info("Stopped the clicker. Press 's' to start again.")
            await asyncio.sleep(0.5)  # Delay to avoid rapid toggling
        return not self.running

    @staticmethod
    def activate_window(window: Any) -> None:
        """
        Activate or bring the target window to the foreground.
        """
        if not window:
            return
        try:
            window.activate()
        except (Exception, ExceptionGroup):
            window.minimize()
            window.restore()

    async def click_on_green(self, screen: Any, rect: Tuple[int, int, int, int]) -> bool:
        """
        Click on green areas, avoiding overlap with bombs (grey) and ice (blue).
        """
        width, height = screen.size
        found_clickable = False

        for x, y in product(range(0, width, 20), range(0, height, 20)):
            r, g, b = screen.getpixel((x, y))

            # Define color ranges for green, bomb (grey), and ice (blue)
            is_green = (b < 120) and (100 <= r <= 180) and (200 <= g <= 255)
            is_bomb = (r, g, b) == (128, 128, 128)  # Grey (bomb)
            is_ice = (r, g, b) == (0, 0, 255)  # Blue (ice)

            # Only click green areas that are not overlapping with bomb or ice
            if is_green and not (is_bomb or is_ice):
                screen_x = rect[0] + x
                screen_y = rect[1] + y
                await self.click(screen_x + 4, screen_y)  # Add random offset
                found_clickable = True
            elif is_green and (is_bomb or is_ice):
                logger.info(f"Skipped green at ({x}, {y}) due to bomb or ice overlap.")
                
        return found_clickable

    async def click_on_play_button(self, screen: Any, rect: Tuple[int, int, int, int]) -> bool:
        """
        Click on the 'Play' button (assuming it has white text).
        """
        width, height = screen.size

        for x, y in product(range(0, width, 20), range(0, height, 20)):
            r, g, b = screen.getpixel((x, y))

            if (r, g, b) == (255, 255, 255):  # White color for the button text
                screen_x = rect[0] + x
                screen_y = rect[1] + y
                await self.click(screen_x, screen_y)
                return True

        return False

    async def run(self) -> None:
        """
        Main loop that controls the clicker.
        """
        try:
            # Try to find the application window (TelegramDesktop or 64Gram)
            window = next(
                (gw.getWindowsWithTitle(opt)
                 for opt in ["TelegramDesktop", "64Gram"]
                 if gw.getWindowsWithTitle(opt)),
                None,
            )

            if not window:
                logger.error(WINDOW_NOT_FOUND)
                return

            logger.info("Initialized Blum script by Tejas")
            logger.info(f"Found blum window: {window[0].title}")
            logger.info("Press 's' to start or stop the program.")

            while True:
                if await self.handle_input():
                    continue

                rect = self.utils.get_rect(window[0])
                self.activate_window(window[0])

                screenshot = self.utils.capture_screenshot(rect)

                # Create tasks for clicking on green areas
                tasks = [self.click_on_green(screenshot, rect) for _ in range(10)]
                await asyncio.gather(*tasks)

                # Attempt to click on the 'Play' button
                await self.click_on_play_button(screenshot, rect)

        except gw.PyGetWindowException as error:
            logger.error(f"The window might have been closed. Window error: {str(error)}.")


# Logging setup
def logging_setup():
    format_info = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <level>{message}</level>"
    logger.remove()

    logger.add(sys.stdout, colorize=True, format=format_info, level="INFO")


logging_setup()


# Main script
async def main() -> None:
    os.system("cls")  # Clear screen for a clean start

    print(AUTOCLICKER_TEXT)  # Display the custom ASCII art with Blum Script by Tejasvi
    print(CREDITS)  # Display the credits with your Telegram link

    clicker = BlumClicker()
    await clicker.run()  # Run the BlumClicker


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting... Looks like Blum needed a break. Come back soon!")
