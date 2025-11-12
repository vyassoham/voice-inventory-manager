import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# =====================================================
# Configuration
# =====================================================
DATA_FILE = "inventory.json"

st.set_page_config(
    page_title="🎤 Voice-Enabled Inventory Manager",
    page_icon="🎙️",
    layout="centered"
)

# =====================================================
# Inventory Manager Logic
# =====================================================

class InventoryManager:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.inventory = self.load()

    def load(self):
        """Load inventory data from file or create new one."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    st.warning("⚠️ Inventory file corrupted. Starting fresh.")
                    return {}
        return {}

    def save(self):
        """Save inventory to JSON file."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.inventory, f, indent=2)

    def add_or_update_stock(self, item, quantity):
        """Add or increase stock."""
        item = item.lower()
        quantity = int(quantity)
        if item in self.inventory:
            self.inventory[item]["stock"] += quantity
        else:
            self.inventory[item] = {"stock": quantity, "alert_level": 0}
        self.save()
        return f"✅ Added/updated '{item}' by {quantity} units. Total = {self.inventory[item]['stock']}."

    def set_alert(self, item, level):
        """Set reorder alert level."""
        item = item.lower()
        level = int(level)
        if item not in self.inventory:
            self.inventory[item] = {"stock": 0, "alert_level": level}
        else:
            self.inventory[item]["alert_level"] = level
        self.save()
        return f"🔔 Reorder alert for '{item}' set to {level}."

    def check_availability(self, item):
        """Return current stock."""
        item = item.lower()
        if item not in self.inventory:
            return f"📦 '{item}' not found in inventory."
        stock = self.inventory[item]["stock"]
        alert = self.inventory[item]["alert_level"]
        symbol = "⚠️" if alert > 0 and stock <= alert else ""
        return f"📊 '{item}' stock: {stock} (Alert at {alert}) {symbol}"

    def remove_item(self, item):
        """Remove an item completely."""
        item = item.lower()
        if item in self.inventory:
            del self.inventory[item]
            self.save()
            return f"🗑️ '{item}' removed from inventory."
        return f"❌ '{item}' not found."

    def get_alerts(self):
        """Return list of low-stock alerts."""
        return {
            item: data
            for item, data in self.inventory.items()
            if data["alert_level"] > 0 and data["stock"] <= data["alert_level"]
        }

    def generate_report(self):
        """Return inventory as pandas DataFrame."""
        if not self.inventory:
            return pd.DataFrame(columns=["Item", "Stock", "Reorder Level"])
        df = pd.DataFrame([
            {"Item": item.title(), "Stock": data["stock"], "Reorder Level": data["alert_level"]}
            for item, data in self.inventory.items()
        ])
        return df

# =====================================================
# Helper Functions
# =====================================================

def parse_command(command: str, inv: InventoryManager):
    """Process voice-like commands and execute actions."""
    command = command.strip().lower()
    parts = command.split()

    if not parts:
        return "❌ Please say a valid command."

    if parts[0] == "add" and len(parts) >= 3:
        try:
            qty = int(parts[1])
            item = " ".join(parts[2:])
            return inv.add_or_update_stock(item, qty)
        except ValueError:
            return "❌ Usage: add <quantity> <item>"

    elif parts[0] == "remove" and len(parts) >= 2:
        item = " ".join(parts[1:])
        return inv.remove_item(item)

    elif parts[0] == "check" and len(parts) >= 2:
        item = " ".join(parts[1:])
        return inv.check_availability(item)

    elif parts[0] == "alert" and len(parts) >= 3:
        try:
            item = parts[1]
            level = int(parts[2])
            return inv.set_alert(item, level)
        except ValueError:
            return "❌ Usage: alert <item> <level>"

    elif parts[0] == "report":
        st.session_state.last_report = inv.generate_report()
        return "📄 Inventory report generated below."

    elif parts[0] == "alerts":
        alerts = inv.get_alerts()
        if not alerts:
            return "✅ No low-stock alerts."
        alert_lines = [f"⚠️ {item}: {data['stock']} (alert at {data['alert_level']})" for item, data in alerts.items()]
        return "\n".join(alert_lines)

    elif parts[0] in ["help", "commands"]:
        return (
            "🗒️ Available commands:\n"
            "• add <quantity> <item>\n"
            "• remove <item>\n"
            "• check <item>\n"
            "• alert <item> <level>\n"
            "• report\n"
            "• alerts\n"
            "• help"
        )

    else:
        return "❌ Command not recognized. Try saying 'help' for a list."

# =====================================================
# Streamlit UI
# =====================================================

st.title("🎙️ Voice-Enabled Inventory Manager")
st.write("Speak or type inventory commands. (Simulated voice input)")

inv = InventoryManager()

if "history" not in st.session_state:
    st.session_state.history = []

# Input box (text acts as voice simulation)
command = st.text_input(
    "🗣️ Say or type a command:",
    placeholder="e.g., add 10 apples / check bananas / alert apples 5 / report"
)

# Process command
if st.button("▶️ Run Command"):
    result = parse_command(command, inv)
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.history.append((timestamp, command, result))

# Display recent command history
st.write("### 💬 Recent Commands")
for time, cmd, res in reversed(st.session_state.history[-5:]):
    st.markdown(f"**[{time}]** 🗣️ `{cmd}` → {res}")

# Show report if generated
if "last_report" in st.session_state:
    st.write("### 📊 Current Inventory")
    st.dataframe(st.session_state.last_report)

    csv = st.session_state.last_report.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Inventory Report", csv, "inventory_report.csv", "text/csv")

# Optional voice output placeholder
st.write("---")
st.caption("🎧 Tip: You can later integrate `speech_recognition` for voice input & `gTTS` for spoken responses.")
