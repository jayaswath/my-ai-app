from datetime import date, timedelta
from pathlib import Path

today = date.today()
yesterday = today - timedelta(days=1)
same_day_last_week = yesterday - timedelta(days=7)
print(today, yesterday, same_day_last_week)
print(yesterday.strftime("%A, %d %b %Y"))

folder = Path("data") / "prompts"
folder.mkdir(parents=True, exist_ok=True)
file = folder / "digest_system.txt"
file.write_text("You are a cloud-kitchen analyst. Be brief.")
print(file, file.exists())
print(file.read_text())