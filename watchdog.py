import subprocess
import time
import sys
import threading

# Trigger phrase to watch for in output
RESTART_TRIGGER = "Timed out while re-/starting screen record, waiting 5 seconds."

# Restart interval in seconds (20 minutes)
RESTART_INTERVAL = 2 * 60


def main():
    print("--- Alune Watchdog Started ---")
    print(f"[Watchdog] Auto-restart interval: {RESTART_INTERVAL // 60} minutes")
    print("Press Ctrl+C to stop the watchdog completely.\n")

    while True:
        try:
            # sys.executable ensures we use the same 'python' (venv) that ran this script
            print(f"[Watchdog] Starting main.py...")

            # Use Popen to capture output in real-time
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1  # Line buffered
            )

            # Timer flag to signal restart
            timer_triggered = threading.Event()

            def timer_callback():
                print("\n[Watchdog] 20-minute timer reached! Restarting main.py...")
                timer_triggered.set()
                if process.poll() is None:
                    process.terminate()

            # Start the 20-minute timer
            timer = threading.Timer(RESTART_INTERVAL, timer_callback)
            timer.daemon = True
            timer.start()

            # Monitor output line by line
            for line in process.stdout:
                print(line, end="")  # Print the line as normal

                # Check if the trigger phrase is in the output
                if RESTART_TRIGGER in line:
                    print("\n[Watchdog] Detected screen record timeout! Restarting main.py...")
                    timer.cancel()
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break

                # Check if timer triggered the restart
                if timer_triggered.is_set():
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break

            # Cancel timer if still running
            timer.cancel()

            process.wait()
            print("\n[Watchdog] Bot process ended. Restarting in 5 seconds...")
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n[Watchdog] Stopping Watchdog. Goodbye!")
            if 'timer' in locals():
                timer.cancel()
            if 'process' in locals() and process.poll() is None:
                process.terminate()
            sys.exit(0)
        except Exception as e:
            print(f"[Watchdog] Unexpected error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()