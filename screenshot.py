
import base64
import cv2
import numpy as np
from ppadb.client import Client as AdbClient


class ScreenshotCapture:
    def __init__(self, emulator_port=5555):
        """
        Emulator ports:
        - BlueStacks -> 5555
        - NoxPlayer -> 62001
        - MEmu -> 21503
        """
        self.adb_client = AdbClient(host="127.0.0.1", port=5037)
        self.emulator_port = emulator_port
        self.device = None

    def connect(self):
        try:
            devices = self.adb_client.devices()

            if not devices:
                raise Exception("No devices found! Make sure emulator is running and ADB is enabled.")

            self.device = devices[0]
            print(f"Connected to device: {self.device.serial}")
            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            print("\nTroubleshooting:")
            print("1. Is your emulator running?")
            print("2. Is ADB enabled in emulator settings?")
            print("3. Try: adb kill-server && adb start-server")
            return False

    def capture_screenshot(self):
        if not self.device:
            raise Exception("Not connected! Call connect() first.")

        try:
            screenshot_bytes = self.device.screencap()

            nparr = np.frombuffer(screenshot_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            height, width = img.shape[:2]
            if width > 1568:
                scale = 1568 / width
                img = cv2.resize(img, None, fx=scale, fy=scale)

            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
            base64_image = base64.b64encode(buffer).decode('utf-8')

            print(f"Screenshot captured ({width}x{height}px)")
            return base64_image

        except Exception as e:
            print(f"Screenshot failed: {e}")
            raise

    def save_screenshot(self, filename="test_screenshot.png"):
        if not self.device:
            raise Exception("Not connected! Call connect() first.")

        screenshot_bytes = self.device.screencap()

        with open(filename, 'wb') as f:
            f.write(screenshot_bytes)

        print(f"Screenshot saved to {filename}")


# Test code - Run this file directly to test
if __name__ == "__main__":
    print("=" * 50)
    print("SCREENSHOT CAPTURE TEST")
    print("=" * 50)


    capture = ScreenshotCapture(emulator_port=5555)


    if capture.connect():
        print("\nTest 1: Saving screenshot to file...")
        capture.save_screenshot("test_screenshot.png")

        print("\nTest 2: Capturing as base64...")
        base64_img = capture.capture_screenshot()
        print(f"✓ Base64 length: {len(base64_img)} characters")

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Check that test_screenshot.png was created")
        print("2. Ready for integration!")
    else:
        print("\n✗ Tests failed - fix connection issues first")
