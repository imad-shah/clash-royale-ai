import base64
import cv2
import numpy as np
import subprocess
import tempfile
import os
import platform
import sys
import config


class ScreenshotCapture:
    def __init__(self, emulator_port=5555):
        self.connected = False
        self.temp_dir = tempfile.gettempdir()
        self.platform = self._detect_platform()

    def _detect_platform(self):
        system = platform.system()

        if system == 'Windows':
            return 'windows'
        elif system == 'Linux':
            # Check if running in WSL
            try:
                with open('/proc/version', 'r') as f:
                    if 'microsoft' in f.read().lower():
                        return 'wsl'
            except:
                pass
            return 'linux'
        else:
            return 'unknown'

    def connect(self):
        try:
            print(f"Platform detected: {self.platform.upper()}")

            if self.platform == 'windows':
                # Native Windows - check if we can import required modules
                try:
                    import win32gui
                    import win32ui
                    import win32con
                    print("Windows screenshot modules available")
                except ImportError:
                    print("WARNING: pywin32 not installed, falling back to PowerShell method")
                    self.platform = 'windows_ps'

            elif self.platform == 'wsl':
                # WSL2 - Test if we can run PowerShell
                result = subprocess.run(
                    ['powershell.exe', '-Command', 'echo "test"'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    raise Exception("PowerShell not accessible from WSL2")
                print("PowerShell access confirmed (WSL2 → Windows)")

            else:
                raise Exception(f"Unsupported platform: {self.platform}")

            if config.CROP_ENABLED:
                x = config.CROP_X
                y = config.CROP_Y
                w = config.CROP_WIDTH
                h = config.CROP_HEIGHT
                print(f"Capture region configured: ({x}, {y}) size {w}x{h}px")
            else:
                print("Full screen capture mode (will capture primary monitor)")

            self.connected = True
            print("Screenshot capture ready!")
            return True

        except Exception as e:
            print(f"Setup failed: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure you have a display connected")
            print("2. On Windows, consider installing pywin32: pip install pywin32")
            print("3. On WSL2, PowerShell must be accessible")
            print("4. Check config.py for valid CROP coordinates")
            return False

    def _capture_windows_native(self):
        import win32gui
        import win32ui
        import win32con
        import win32api
        from PIL import Image

        # Get screen dimensions
        hdesktop = win32gui.GetDesktopWindow()

        if config.CROP_ENABLED:
            left = config.CROP_X
            top = config.CROP_Y
            width = config.CROP_WIDTH
            height = config.CROP_HEIGHT
        else:
            left = 0
            top = 0
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

        # Create device context
        desktop_dc = win32gui.GetWindowDC(hdesktop)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        mem_dc = img_dc.CreateCompatibleDC()

        # Create bitmap
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)

        # Copy screen to bitmap
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

        # Convert to PIL Image then numpy array
        bmpinfo = screenshot.GetInfo()
        bmpstr = screenshot.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Cleanup
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())
        img_dc.DeleteDC()
        win32gui.ReleaseDC(hdesktop, desktop_dc)

        return img

    def _capture_powershell(self):
        # Create temporary file path
        if self.platform == 'wsl':
            temp_file = os.path.join(self.temp_dir, 'wsl_screenshot.png').replace('/', '\\')
        else:
            temp_file = os.path.join(self.temp_dir, 'screenshot.png')

        # PowerShell script to capture screenshot
        if config.CROP_ENABLED:
            x = config.CROP_X
            y = config.CROP_Y
            w = config.CROP_WIDTH
            h = config.CROP_HEIGHT
            ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap {w}, {h}
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen({x}, {y}, 0, 0, $bitmap.Size)
$bitmap.Save('{temp_file}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""
        else:
            ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bitmap.Save('{temp_file}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""

        # Execute PowerShell script
        ps_cmd = 'powershell.exe' if self.platform == 'wsl' else 'powershell'
        subprocess.run(
            [ps_cmd, '-Command', ps_script],
            capture_output=True,
            timeout=10
        )

        # Read the screenshot file
        read_path = temp_file.replace('\\', '/') if self.platform == 'wsl' else temp_file
        img = cv2.imread(read_path)
        if img is None:
            raise Exception(f"Failed to read screenshot from {read_path}")

        # Clean up temp file
        try:
            os.remove(read_path)
        except:
            pass

        return img

    def capture_screenshot(self):
        if not self.connected:
            raise Exception("Not connected! Call connect() first.")

        try:
            # Capture based on platform
            if self.platform == 'windows':
                img = self._capture_windows_native()
            elif self.platform in ['wsl', 'windows_ps']:
                img = self._capture_powershell()
            else:
                raise Exception(f"Unsupported platform: {self.platform}")

            height, width = img.shape[:2]

            # Resize if too large
            if width > 1568:
                scale = 1568 / width
                img = cv2.resize(img, None, fx=scale, fy=scale)
                print(f"Screenshot captured and resized: {width}x{height}px -> {img.shape[1]}x{img.shape[0]}px")
            else:
                print(f"Screenshot captured: {width}x{height}px")

            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
            base64_image = base64.b64encode(buffer).decode('utf-8')

            return base64_image

        except Exception as e:
            print(f"Screenshot failed: {e}")
            raise

    def save_screenshot(self, filename="test_screenshot.png"):
        """Capture screenshot and save to file"""
        if not self.connected:
            raise Exception("Not connected! Call connect() first.")

        try:
            # Capture based on platform
            if self.platform == 'windows':
                img = self._capture_windows_native()
            elif self.platform in ['wsl', 'windows_ps']:
                img = self._capture_powershell()
            else:
                raise Exception(f"Unsupported platform: {self.platform}")

            cv2.imwrite(filename, img)
            print(f"Screenshot saved to {filename}")

        except Exception as e:
            print(f"Failed to save screenshot: {e}")
            raise


# Test code - Run this file directly to test
if __name__ == "__main__":
    print("=" * 50)
    print("SCREENSHOT CAPTURE TEST")
    print("=" * 50)

    capture = ScreenshotCapture()

    if capture.connect():
        print("\nTest 1: Saving screenshot to file...")
        capture.save_screenshot("test_screenshot.png")

        print("\nTest 2: Capturing as base64...")
        base64_img = capture.capture_screenshot()
        print(f"Base64 length: {len(base64_img)} characters")

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Check that test_screenshot.png was created")
        print("2. Adjust CROP_X, CROP_Y, CROP_WIDTH, CROP_HEIGHT in config.py")
        print("3. Ready for integration!")
    else:
        print("\n✗ Tests failed - check configuration")
