import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import re

# =====================================================
# ADVANCED CONFIGURATION
# =====================================================
DATA_FILE = "inventory_advanced.json"
HISTORY_FILE = "transaction_history.json"
CATEGORIES_FILE = "categories.json"

st.set_page_config(
    page_title="🎙️ SmartStock Pro - AI Inventory Manager",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .alert-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .success-card {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .command-history {
        background: #f8f9fa;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 0.3rem 0;
        border-left: 3px solid #667eea;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# ADVANCED INVENTORY MANAGEMENT CLASS
# =====================================================
class AdvancedInventoryManager:
    def __init__(self, data_file=DATA_FILE, history_file=HISTORY_FILE, categories_file=CATEGORIES_FILE):
        self.data_file = data_file
        self.history_file = history_file
        self.categories_file = categories_file
        self.inventory = self.load()
        self.history = self.load_history()
        self.categories = self.load_categories()

    def load(self):
        """Load inventory data with error handling."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                st.warning("⚠️ Inventory file corrupted. Starting fresh.")
        return {}

    def load_history(self):
        """Load transaction history."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def load_categories(self):
        """Load item categories."""
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save(self):
        """Save all data."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.inventory, f, indent=2)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)
        with open(self.categories_file, "w", encoding="utf-8") as f:
            json.dump(self.categories, f, indent=2)

    def log_transaction(self, action, item, quantity, notes=""):
        """Log all transactions for audit trail."""
        transaction = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "item": item,
            "quantity": quantity,
            "notes": notes,
            "stock_after": self.inventory.get(item, {}).get("stock", 0)
        }
        self.history.append(transaction)
        if len(self.history) > 1000:  # Keep last 1000 transactions
            self.history = self.history[-1000:]

    def add_or_update_stock(self, item, quantity, category="General", unit="units", cost_per_unit=0, supplier="", notes=""):
        """Add or increase stock with enhanced metadata."""
        item = item.lower().strip()
        quantity = int(quantity)
        
        if item in self.inventory:
            self.inventory[item]["stock"] += quantity
            self.inventory[item]["last_updated"] = datetime.now().isoformat()
            if cost_per_unit > 0:
                # Calculate weighted average cost
                old_total_value = self.inventory[item].get("total_value", 0)
                new_total_value = old_total_value + (quantity * cost_per_unit)
                new_stock = self.inventory[item]["stock"]
                self.inventory[item]["avg_cost"] = new_total_value / new_stock if new_stock > 0 else cost_per_unit
                self.inventory[item]["total_value"] = new_total_value
        else:
            self.inventory[item] = {
                "stock": quantity,
                "alert_level": 0,
                "category": category,
                "unit": unit,
                "avg_cost": cost_per_unit,
                "total_value": quantity * cost_per_unit,
                "supplier": supplier,
                "date_added": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self.categories[item] = category
        
        self.log_transaction("ADD", item, quantity, notes)
        self.save()
        
        total_stock = self.inventory[item]["stock"]
        value = self.inventory[item].get("total_value", 0)
        return f"✅ Added {quantity} {unit} of '{item}'. Total: {total_stock} {unit} (Value: ${value:.2f})"

    def reduce_stock(self, item, quantity, reason="Sale", notes=""):
        """Reduce stock (for sales, waste, etc.)."""
        item = item.lower().strip()
        quantity = int(quantity)
        
        if item not in self.inventory:
            return f"❌ '{item}' not found in inventory."
        
        current_stock = self.inventory[item]["stock"]
        if quantity > current_stock:
            return f"⚠️ Cannot reduce '{item}' by {quantity}. Only {current_stock} available."
        
        self.inventory[item]["stock"] -= quantity
        self.inventory[item]["last_updated"] = datetime.now().isoformat()
        
        # Update total value
        avg_cost = self.inventory[item].get("avg_cost", 0)
        self.inventory[item]["total_value"] = self.inventory[item]["stock"] * avg_cost
        
        self.log_transaction("REDUCE", item, -quantity, f"{reason}: {notes}")
        self.save()
        
        remaining = self.inventory[item]["stock"]
        return f"📉 Reduced '{item}' by {quantity}. Remaining: {remaining}"

    def set_alert(self, item, level):
        """Set reorder alert level."""
        item = item.lower().strip()
        level = int(level)
        
        if item not in self.inventory:
            self.inventory[item] = {
                "stock": 0,
                "alert_level": level,
                "category": "General",
                "unit": "units",
                "date_added": datetime.now().isoformat()
            }
        else:
            self.inventory[item]["alert_level"] = level
        
        self.log_transaction("ALERT_SET", item, 0, f"Alert level set to {level}")
        self.save()
        return f"🔔 Reorder alert for '{item}' set to {level}."

    def check_availability(self, item):
        """Return detailed stock information."""
        item = item.lower().strip()
        
        if item not in self.inventory:
            # Fuzzy search for similar items
            similar = [k for k in self.inventory.keys() if item in k or k in item]
            if similar:
                suggestions = ", ".join([f"'{s}'" for s in similar[:3]])
                return f"📦 '{item}' not found. Did you mean: {suggestions}?"
            return f"📦 '{item}' not found in inventory."
        
        data = self.inventory[item]
        stock = data["stock"]
        alert = data["alert_level"]
        unit = data.get("unit", "units")
        value = data.get("total_value", 0)
        category = data.get("category", "General")
        
        status = "🟢 Good"
        if alert > 0:
            if stock == 0:
                status = "🔴 Out of Stock"
            elif stock <= alert:
                status = "🟡 Low Stock"
        
        return (f"📊 **{item.title()}**\n"
                f"├─ Stock: {stock} {unit}\n"
                f"├─ Status: {status}\n"
                f"├─ Reorder Level: {alert}\n"
                f"├─ Category: {category}\n"
                f"└─ Value: ${value:.2f}")

    def remove_item(self, item):
        """Remove an item completely."""
        item = item.lower().strip()
        if item in self.inventory:
            del self.inventory[item]
            self.log_transaction("DELETE", item, 0, "Item removed from system")
            self.save()
            return f"🗑️ '{item}' removed from inventory."
        return f"❌ '{item}' not found."

    def get_alerts(self):
        """Return list of low-stock alerts."""
        alerts = {}
        for item, data in self.inventory.items():
            if data["alert_level"] > 0 and data["stock"] <= data["alert_level"]:
                urgency = "CRITICAL" if data["stock"] == 0 else "LOW"
                alerts[item] = {**data, "urgency": urgency}
        return alerts

    def get_analytics(self):
        """Generate comprehensive analytics."""
        if not self.inventory:
            return None
        
        total_items = len(self.inventory)
        total_value = sum(item.get("total_value", 0) for item in self.inventory.values())
        total_stock = sum(item.get("stock", 0) for item in self.inventory.values())
        low_stock_count = len(self.get_alerts())
        
        # Category breakdown
        category_data = defaultdict(lambda: {"count": 0, "value": 0, "stock": 0})
        for item, data in self.inventory.items():
            cat = data.get("category", "General")
            category_data[cat]["count"] += 1
            category_data[cat]["value"] += data.get("total_value", 0)
            category_data[cat]["stock"] += data.get("stock", 0)
        
        return {
            "total_items": total_items,
            "total_value": total_value,
            "total_stock": total_stock,
            "low_stock_count": low_stock_count,
            "categories": dict(category_data)
        }

    def generate_report(self, category_filter=None):
        """Return inventory as pandas DataFrame with filters."""
        if not self.inventory:
            return pd.DataFrame(columns=["Item", "Stock", "Unit", "Category", "Value", "Status"])
        
        data = []
        for item, details in self.inventory.items():
            if category_filter and details.get("category") != category_filter:
                continue
            
            stock = details["stock"]
            alert = details["alert_level"]
            status = "🟢 Good"
            if alert > 0:
                if stock == 0:
                    status = "🔴 Out of Stock"
                elif stock <= alert:
                    status = "🟡 Low Stock"
            
            data.append({
                "Item": item.title(),
                "Stock": stock,
                "Unit": details.get("unit", "units"),
                "Category": details.get("category", "General"),
                "Value": f"${details.get('total_value', 0):.2f}",
                "Reorder Level": alert,
                "Supplier": details.get("supplier", "N/A"),
                "Status": status
            })
        
        return pd.DataFrame(data)

    def search_items(self, query):
        """Search items by name or category."""
        query = query.lower()
        results = []
        for item, data in self.inventory.items():
            if query in item or query in data.get("category", "").lower():
                results.append(item)
        return results

    def get_transaction_history(self, days=7, item=None):
        """Get recent transaction history."""
        cutoff = datetime.now() - timedelta(days=days)
        filtered = []
        
        for trans in self.history:
            trans_date = datetime.fromisoformat(trans["timestamp"])
            if trans_date >= cutoff:
                if item is None or trans["item"] == item.lower():
                    filtered.append(trans)
        
        return filtered

# =====================================================
# VOICE UTILITIES WITH BETTER ERROR HANDLING
# =====================================================
def listen_command():
    """Capture voice input with improved error handling."""
    r = sr.Recognizer()
    r.energy_threshold = 4000
    r.dynamic_energy_threshold = True
    
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak clearly!")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, phrase_time_limit=7, timeout=10)
        
        with st.spinner("🔄 Processing speech..."):
            command = r.recognize_google(audio)
            st.success(f"✅ Recognized: **{command}**")
            return command.lower()
    except sr.WaitTimeoutError:
        st.warning("⏱️ No speech detected. Please try again.")
        return ""
    except sr.UnknownValueError:
        st.warning("❌ Could not understand. Please speak clearly.")
        return ""
    except sr.RequestError as e:
        st.error(f"⚠️ Speech service error: {e}")
        return ""
    except Exception as e:
        st.error(f"🔴 Unexpected error: {e}")
        return ""

def speak(text):
    """Convert text to speech with audio player."""
    try:
        # Clean text for speech
        clean_text = text.replace("*", "").replace("#", "").replace("├", "").replace("└", "").replace("─", "")
        tts = gTTS(text=clean_text, lang="en", slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.warning(f"🔇 Audio playback unavailable: {e}")

# =====================================================
# ADVANCED COMMAND PARSER WITH NLP
# =====================================================
def parse_command(command: str, inv: AdvancedInventoryManager):
    """Process voice/text commands with natural language understanding."""
    command = command.strip().lower()
    
    # Extract numbers from command
    numbers = re.findall(r'\d+', command)
    
    # Natural language patterns
    if any(word in command for word in ["add", "stock", "receive", "received"]):
        if len(numbers) >= 1:
            try:
                qty = int(numbers[0])
                # Extract item name (everything after the number)
                parts = command.split(str(qty), 1)
                if len(parts) > 1:
                    item = parts[1].strip()
                    # Remove common words
                    item = re.sub(r'\b(of|pieces|units|to|the|a|an)\b', '', item).strip()
                    if item:
                        return inv.add_or_update_stock(item, qty)
            except:
                pass
        return "❌ Usage: add [quantity] [item name] (e.g., 'add 50 apples')"
    
    elif any(word in command for word in ["sell", "sold", "remove", "take out", "reduce"]):
        if len(numbers) >= 1:
            try:
                qty = int(numbers[0])
                parts = command.split(str(qty), 1)
                if len(parts) > 1:
                    item = parts[1].strip()
                    item = re.sub(r'\b(of|pieces|units|from|the|a|an)\b', '', item).strip()
                    if item:
                        return inv.reduce_stock(item, qty, reason="Sale")
            except:
                pass
        return "❌ Usage: sell [quantity] [item name]"
    
    elif any(word in command for word in ["check", "how many", "status", "stock of"]):
        # Extract item name
        item = command
        for word in ["check", "how many", "status", "stock of", "what's the stock of"]:
            item = item.replace(word, "").strip()
        item = re.sub(r'\b(do we have|are there|is there)\b', '', item).strip()
        if item:
            return inv.check_availability(item)
        return "❌ Please specify an item to check."
    
    elif any(word in command for word in ["alert", "reorder", "minimum"]):
        if len(numbers) >= 1:
            try:
                level = int(numbers[0])
                item = re.sub(r'\d+', '', command).strip()
                item = re.sub(r'\b(alert|reorder|set|level|minimum|for|at)\b', '', item).strip()
                if item:
                    return inv.set_alert(item, level)
            except:
                pass
        return "❌ Usage: alert [item] [level] (e.g., 'alert apples 10')"
    
    elif "delete" in command or "remove item" in command:
        item = command.replace("delete", "").replace("remove item", "").strip()
        if item:
            return inv.remove_item(item)
        return "❌ Please specify an item to delete."
    
    elif "report" in command or "show inventory" in command:
        st.session_state.show_report = True
        return "📄 Inventory report displayed below."
    
    elif "alerts" in command or "low stock" in command:
        alerts = inv.get_alerts()
        if not alerts:
            return "✅ All items are well-stocked!"
        alert_text = "⚠️ **Low Stock Alerts:**\n"
        for item, data in alerts.items():
            alert_text += f"• {item.title()}: {data['stock']} {data.get('unit', 'units')} ({data['urgency']})\n"
        return alert_text
    
    elif any(word in command for word in ["help", "commands", "what can you do"]):
        return """🗒️ **Available Commands:**
        
**Stock Management:**
• "Add 50 apples" - Add items to inventory
• "Sell 10 bananas" - Reduce stock
• "Check oranges" - View item status
• "Delete mangoes" - Remove item
        
**Alerts & Reports:**
• "Alert apples 20" - Set reorder level
• "Show alerts" - View low stock items
• "Generate report" - Full inventory view
        
**Analytics:**
• "Show analytics" - View dashboard
• "Search fruit" - Find items

Just speak naturally! 🎤"""
    
    else:
        # Try fuzzy matching for common variations
        return "❌ Command not recognized. Say 'help' for available commands."

# =====================================================
# STREAMLIT UI - MAIN APPLICATION
# =====================================================
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎙️ SmartStock Pro</h1>
        <p>Advanced AI-Powered Inventory Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize
    inv = AdvancedInventoryManager()
    
    if "history" not in st.session_state:
        st.session_state.history = []
    if "show_report" not in st.session_state:
        st.session_state.show_report = False
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Control Panel")
        
        # Quick Stats
        analytics = inv.get_analytics()
        if analytics:
            st.metric("📦 Total Items", analytics["total_items"])
            st.metric("💰 Total Value", f"${analytics['total_value']:.2f}")
            st.metric("⚠️ Low Stock Items", analytics["low_stock_count"])
        
        st.divider()
        
        # Mode Selection
        st.subheader("🎛️ Input Mode")
        mode = st.radio("Choose Mode:", ["🎤 Voice", "⌨️ Text", "📊 Analytics"], label_visibility="collapsed")
        
        st.divider()
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        if st.button("📄 Generate Report", use_container_width=True):
            st.session_state.show_report = True
        
        if st.button("🔔 View Alerts", use_container_width=True):
            alerts = inv.get_alerts()
            if alerts:
                for item, data in alerts.items():
                    st.warning(f"⚠️ **{item.title()}**: {data['stock']} {data.get('unit', 'units')}")
            else:
                st.success("✅ No alerts!")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
        
        st.divider()
        
        # Settings
        with st.expander("⚙️ Advanced Settings"):
            st.checkbox("🔊 Enable Voice Feedback", value=True, key="voice_feedback")
            st.checkbox("📊 Auto-show Analytics", value=False, key="auto_analytics")
            st.number_input("📅 History Days", min_value=1, max_value=90, value=7, key="history_days")
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if mode == "🎤 Voice":
            st.subheader("🎤 Voice Command Center")
            st.info("💡 **Tip:** Speak naturally! Try: 'Add 50 apples' or 'Check banana stock'")
            
            if st.button("🎙️ Start Voice Command", use_container_width=True, type="primary"):
                command = listen_command()
                if command:
                    result = parse_command(command, inv)
                    if st.session_state.get("voice_feedback", True):
                        speak(result)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    st.session_state.history.append((timestamp, command, result))
                    st.rerun()
        
        elif mode == "⌨️ Text":
            st.subheader("⌨️ Text Command Interface")
            command = st.text_input(
                "Enter Command:",
                placeholder="e.g., add 100 oranges, check apples, alert bananas 20",
                key="text_command"
            )
            
            col_a, col_b = st.columns([3, 1])
            with col_a:
                execute = st.button("▶️ Execute Command", use_container_width=True, type="primary")
            with col_b:
                if st.button("❓ Help", use_container_width=True):
                    result = parse_command("help", inv)
                    st.info(result)
            
            if execute and command:
                result = parse_command(command, inv)
                if st.session_state.get("voice_feedback", True):
                    speak(result)
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.history.append((timestamp, command, result))
                st.success(result)
        
        else:  # Analytics Mode
            st.subheader("📊 Analytics Dashboard")
            analytics = inv.get_analytics()
            
            if analytics:
                # KPI Cards
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("📦 Total Items", analytics["total_items"])
                kpi2.metric("💰 Total Value", f"${analytics['total_value']:.2f}")
                kpi3.metric("📈 Total Stock", analytics["total_stock"])
                kpi4.metric("⚠️ Alerts", analytics["low_stock_count"])
                
                st.divider()
                
                # Category Distribution
                if analytics["categories"]:
                    st.subheader("📂 Category Distribution")
                    
                    cat_df = pd.DataFrame([
                        {"Category": cat, "Items": data["count"], "Value": data["value"], "Stock": data["stock"]}
                        for cat, data in analytics["categories"].items()
                    ])
                    
                    fig = px.pie(cat_df, values="Items", names="Category", title="Items by Category")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    fig2 = px.bar(cat_df, x="Category", y="Value", title="Value by Category", color="Category")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("📭 No data available yet. Start adding items to see analytics!")
    
    with col2:
        st.subheader("💬 Command History")
        if st.session_state.history:
            for time, cmd, res in reversed(st.session_state.history[-10:]):
                with st.container():
                    st.markdown(f"""
                    <div class="command-history">
                        <small><b>[{time}]</b></small><br>
                        <b>🗣️ Command:</b> {cmd}<br>
                        <b>📝 Result:</b> {res[:100]}...
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📭 No commands yet. Start by speaking or typing!")
    
    # Report Section
    if st.session_state.get("show_report", False):
        st.divider()
        st.subheader("📊 Inventory Report")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            categories = list(set([data.get("category", "General") for data in inv.inventory.values()]))
            category_filter = st.selectbox("Filter by Category:", ["All"] + categories)
        
        df = inv.generate_report(None if category_filter == "All" else category_filter)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download options
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download CSV",
                    csv,
                    f"inventory_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            with col2:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Inventory')
                excel_buffer.seek(0)
                st.download_button(
                    "⬇️ Download Excel",
                    excel_buffer,
                    f"inventory_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.info("📭 No items in inventory yet.")
    
    # Footer
    st.divider()
    st.caption("🎧 **Pro Tip:** Speak naturally! The system understands commands like 'Add 100 apples', 'How many oranges do we have?', or 'Set alert for bananas at 20'")

if __name__ == "__main__":
    main()

