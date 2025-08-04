from discordrp import Presence
import time

client_id = "1401895339702747156"

with Presence(client_id) as presence:
    print("RPC đã hoạt động")
    presence.set({
        "state": "Saki Renewed",
        "details": "discord.gg/vietrhythm",
        "timestamps": {"start": int(time.time())},
        "large_text": "Rena gay",
        "buttons": [
            {"label": "Discord", "url": "https://discord.gg/vietrhythm"}
        ]
    })
    print("Rich Presence updated!")
    while True:
        time.sleep(15) # Update every 15 seconds