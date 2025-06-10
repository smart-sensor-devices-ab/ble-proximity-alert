import platform
import serial
import time
import subprocess
import winsound

# ==== CONFIGURATION ====
# SERIAL_PORT = '/dev/cu.usbmodem4048FDEBA6D01'  # Update as needed
SERIAL_PORT = "COM8"  # Update as needed
BAUD_RATE = 9600
TARGET_DEVICE_MAC = "D0:76:50:80:15:32"
SOUND_FILE = "beep.wav"  # Must exist in the same folder

# RSSI filter threshold: Acceptable range is -1 to -99
RSSI_FILTER_THRESHOLD = "60"  # You can input without '-' sign
# ========================


def play_beep():
    try:
        if platform.system() == "Windows":
            winsound.PlaySound(SOUND_FILE, winsound.SND_FILENAME)
        else:
            subprocess.call(["afplay", SOUND_FILE])  # For macOS
    except Exception as e:
        print(f"Failed to play sound: {e}")


def connect_to_bleuio():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)

        # Send basic AT to wake up
        ser.write(b"AT\r\n")
        time.sleep(0.5)

        # Ensure threshold has leading '-'
        rssi_value = RSSI_FILTER_THRESHOLD
        if not rssi_value.startswith("-"):
            rssi_value = "-" + rssi_value

        # Send AT+FRSSI command
        command = f"AT+FRSSI={rssi_value}\r\n".encode()
        ser.write(command)
        print(f"RSSI filter set to {rssi_value} dBm\n")
        time.sleep(0.5)

        return ser
    except Exception as e:
        print(f"Error connecting to BleuIO: {e}")
        return None


def scan_for_device(ser):
    ser.write(b"AT+GAPSCAN=3\r\n")
    end_time = time.time() + 5

    while time.time() < end_time:
        if ser.in_waiting:
            line = ser.readline().decode(errors="ignore").strip()
            print(line)
            if TARGET_DEVICE_MAC in line:
                print("Target device found! Triggering alert...")
                play_beep()

    print("Scan complete.\n")


def main():
    ser = connect_to_bleuio()
    if not ser:
        return

    print("Connected to BleuIO. Starting periodic scan...\n")

    while True:
        scan_for_device(ser)
        time.sleep(30)


if __name__ == "__main__":
    main()
