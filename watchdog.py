import subprocess
import time
import sys


def main():
    print("--- Alune Watchdog Started ---")
    print("Press Ctrl+C to stop the watchdog completely.\n")

    restart_count = 0  # number of restarts performed

    while True:
        try:
            # sys.executable ensures we use the same 'python' (venv) that ran this script
            print(f"[Watchdog] Starting main.py...")
            subprocess.run([sys.executable, "main.py"])

            restart_count += 1
            print(f"\n[Watchdog] Bot process ended. Restart count: {restart_count}. Restarting in 5 seconds...")
            time.sleep(5)

        except KeyboardInterrupt:
            print(f"\n[Watchdog] Stopping Watchdog. Total restarts: {restart_count}. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"[Watchdog] Unexpected error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()