"""
GUI Interface Module

Graphical user interface using Tkinter.

Features:
- Voice command button
- Text input field
- Inventory display
- Statistics panel
- Real-time updates
"""

from typing import Dict, Any
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from utils.logger import get_logger
from core.voice_engine import VoiceEngine
from core.inventory_engine import InventoryEngine
import threading


class GUIInterface:
    """
    Graphical user interface for voice inventory system.
    """

    def __init__(
        self,
        voice_engine: VoiceEngine,
        inventory_engine: InventoryEngine,
        config: Dict[str, Any]
    ):
        """
        Initialize GUI interface.

        Args:
            voice_engine: Voice engine instance
            inventory_engine: Inventory engine instance
            config: Configuration dictionary
        """
        self.voice_engine = voice_engine
        self.inventory_engine = inventory_engine
        self.config = config
        self.logger = get_logger(__name__)

        self.root = None
        self.is_listening = False

    def run(self):
        """Run the GUI application."""
        self.root = tk.Tk()
        self.root.title("Voice Inventory Manager")
        self.root.geometry("900x700")

        self._create_widgets()
        self._setup_layout()

        # Initial calibration
        self.voice_engine.calibrate_noise()

        # Load initial data
        self.refresh_inventory()

        self.root.mainloop()

    def _create_widgets(self):
        """Create GUI widgets."""
        # Title
        self.title_label = tk.Label(
            self.root,
            text="Voice Inventory Manager",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=10
        )

        # Control Frame
        self.control_frame = tk.Frame(self.root, bg="#ecf0f1", pady=10)

        # Voice button
        self.voice_button = tk.Button(
            self.control_frame,
            text="🎤 Voice Command",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            command=self.handle_voice_command,
            width=20,
            height=2
        )

        # Text input
        self.text_input = tk.Entry(
            self.control_frame,
            font=("Arial", 12),
            width=40
        )
        self.text_input.bind('<Return>', lambda e: self.handle_text_command())

        # Send button
        self.send_button = tk.Button(
            self.control_frame,
            text="Send",
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            command=self.handle_text_command,
            width=10
        )

        # Refresh button
        self.refresh_button = tk.Button(
            self.control_frame,
            text="🔄 Refresh",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            command=self.refresh_inventory,
            width=10
        )

        # Response area
        self.response_frame = tk.LabelFrame(
            self.root,
            text="Response",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            pady=5
        )

        self.response_text = scrolledtext.ScrolledText(
            self.response_frame,
            font=("Arial", 10),
            height=6,
            wrap=tk.WORD,
            bg="#ffffff"
        )

        # Inventory display
        self.inventory_frame = tk.LabelFrame(
            self.root,
            text="Inventory",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            pady=5
        )

        # Treeview for inventory
        columns = ("Name", "Category", "Quantity", "Price", "Total Value")
        self.inventory_tree = ttk.Treeview(
            self.inventory_frame,
            columns=columns,
            show="headings",
            height=15
        )

        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=150)

        # Scrollbar for treeview
        self.tree_scroll = ttk.Scrollbar(
            self.inventory_frame,
            orient="vertical",
            command=self.inventory_tree.yview
        )
        self.inventory_tree.configure(yscrollcommand=self.tree_scroll.set)

        # Statistics frame
        self.stats_frame = tk.LabelFrame(
            self.root,
            text="Statistics",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            pady=5
        )

        self.stats_label = tk.Label(
            self.stats_frame,
            text="",
            font=("Arial", 10),
            bg="#ecf0f1",
            justify=tk.LEFT,
            anchor="w"
        )

    def _setup_layout(self):
        """Setup widget layout."""
        # Title
        self.title_label.pack(fill=tk.X)

        # Control frame
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)

        self.voice_button.pack(side=tk.LEFT, padx=5)
        self.text_input.pack(side=tk.LEFT, padx=5)
        self.send_button.pack(side=tk.LEFT, padx=5)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        # Response area
        self.response_frame.pack(fill=tk.X, padx=10, pady=5)
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Inventory display
        self.inventory_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Statistics
        self.stats_frame.pack(fill=tk.X, padx=10, pady=5)
        self.stats_label.pack(fill=tk.BOTH, padx=5, pady=5)

    def handle_voice_command(self):
        """Handle voice command button click."""
        if self.is_listening:
            return

        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=self._voice_command_thread)
        thread.daemon = True
        thread.start()

    def _voice_command_thread(self):
        """Voice command thread."""
        self.is_listening = True
        self.update_response("🎤 Listening for command...", clear=True)

        # Update button
        self.voice_button.config(bg="#e74c3c", text="🎤 Listening...")

        try:
            # Listen for command
            text = self.voice_engine.listen_for_command(timeout=5)

            if text:
                self.update_response(f"You said: {text}\n", append=True)

                # Process command
                result = self.voice_engine.process_command(text)

                # Display result
                self.update_response(result['response'], append=True)

                # Refresh inventory
                self.refresh_inventory()
            else:
                self.update_response("No speech detected.", append=True)

        except Exception as e:
            self.logger.error(f"Voice command error: {e}")
            self.update_response(f"Error: {e}", append=True)

        finally:
            self.is_listening = False
            self.voice_button.config(bg="#27ae60", text="🎤 Voice Command")

    def handle_text_command(self):
        """Handle text command."""
        text = self.text_input.get().strip()

        if not text:
            return

        self.update_response(f"Command: {text}\n", clear=True)

        # Process command
        result = self.voice_engine.process_text_command(text)

        # Display result
        self.update_response(result['response'], append=True)

        # Clear input
        self.text_input.delete(0, tk.END)

        # Refresh inventory
        self.refresh_inventory()

    def update_response(self, text: str, clear: bool = False, append: bool = False):
        """
        Update response text area.

        Args:
            text: Text to display
            clear: Clear existing text
            append: Append to existing text
        """
        if clear:
            self.response_text.delete(1.0, tk.END)

        if append:
            self.response_text.insert(tk.END, text + "\n")
        else:
            if not clear:
                self.response_text.delete(1.0, tk.END)
            self.response_text.insert(1.0, text)

        self.response_text.see(tk.END)

    def refresh_inventory(self):
        """Refresh inventory display."""
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        # Get all items
        items = self.inventory_engine.get_all_items()

        # Add items to treeview
        for item in items:
            total_value = item['quantity'] * item['unit_price']
            self.inventory_tree.insert(
                "",
                tk.END,
                values=(
                    item['name'],
                    item['category'],
                    item['quantity'],
                    f"${item['unit_price']:.2f}",
                    f"${total_value:.2f}"
                )
            )

        # Update statistics
        self.update_statistics()

    def update_statistics(self):
        """Update statistics display."""
        stats = self.inventory_engine.get_statistics()

        stats_text = f"""
Total Items: {stats['total_items']}
Total Quantity: {stats['total_quantity']}
Total Value: ${stats['total_value']:.2f}
Categories: {stats['categories']}
Low Stock Items: {stats['low_stock_count']}
        """

        self.stats_label.config(text=stats_text.strip())
