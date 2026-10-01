import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path


APP_TITLE = "UserGate Rule Apply Tracker"
STATE_FILE = Path(__file__).with_name("rule_tracker_state.json")
LOG_FILE = Path(__file__).with_name("rule_tracker.log")


class RuleTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x650")
        self.root.minsize(700, 450)

        self.rules = {}          # filename -> {name, applied, applied_at}
        self.scan_folder = None

        self.load_state()
        self.build_ui()
        self.refresh_stats()
        self.render_rules()

    # ---------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------

    def load_state(self):
        if not STATE_FILE.exists():
            return

        try:
            with STATE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)

            self.scan_folder = data.get("scan_folder")
            self.rules = data.get("rules", {})

        except Exception as e:
            messagebox.showwarning(
                "State file",
                f"Could not load saved state:\n{e}"
            )

    def save_state(self):
        data = {
            "scan_folder": self.scan_folder,
            "rules": self.rules
        }

        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def log_change(self, filename, applied, timestamp):
        action = "APPLIED" if applied else "UNAPPLIED"

        line = (
            f"{timestamp} | {action} | {filename}\n"
        )

        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line)

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def build_ui(self):
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")

        ttk.Button(
            top,
            text="Scan folder with rules",
            command=self.scan_rules
        ).pack(side="left")

        self.folder_label = ttk.Label(
            top,
            text="No folder scanned"
        )
        self.folder_label.pack(
            side="left",
            padx=15
        )

        self.stats_label = ttk.Label(
            self.root,
            text="",
            font=("Segoe UI", 14, "bold")
        )
        self.stats_label.pack(
            fill="x",
            padx=15,
            pady=(5, 10)
        )

        # Scrollable rule list
        container = ttk.Frame(self.root)
        container.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=5
        )

        self.canvas = tk.Canvas(
            container,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.rules_frame = ttk.Frame(self.canvas)

        self.rules_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.rules_frame,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Make inner frame follow canvas width
        self.canvas.bind(
            "<Configure>",
            self.resize_inner_frame
        )

        self.root.bind_all(
            "<MouseWheel>",
            self.mousewheel
        )

        bottom = ttk.Frame(
            self.root,
            padding=10
        )
        bottom.pack(fill="x")

        ttk.Button(
            bottom,
            text="Open log",
            command=self.open_log
        ).pack(side="left")

        ttk.Button(
            bottom,
            text="Reset applied status",
            command=self.reset_status
        ).pack(side="right")

    def resize_inner_frame(self, event):
        self.canvas.itemconfigure(
            self.canvas_window,
            width=event.width
        )

    def mousewheel(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # ---------------------------------------------------------
    # Scanning
    # ---------------------------------------------------------

    def scan_rules(self):
        folder = filedialog.askdirectory(
            title="Select folder containing classified rules"
        )

        if not folder:
            return

        folder = Path(folder)

        # We treat every .txt rule file as one whole rule.
        # MANUAL_REVIEW.txt is intentionally excluded.
        files = sorted(
            p for p in folder.glob("*.txt")
            if p.name.upper() != "MANUAL_REVIEW.TXT"
        )

        if not files:
            messagebox.showinfo(
                "Scan",
                "No .txt rule files were found."
            )
            return

        old_rules = self.rules.copy()
        new_rules = {}

        for file in files:
            key = str(file.resolve())

            # Preserve applied state if the same file was scanned before.
            previous = old_rules.get(key, {})

            new_rules[key] = {
                "name": file.name,
                "path": key,
                "applied": previous.get("applied", False),
                "applied_at": previous.get("applied_at")
            }

        self.rules = new_rules
        self.scan_folder = str(folder.resolve())

        self.save_state()
        self.folder_label.config(
            text=f"{folder}  ({len(files)} rules)"
        )

        self.render_rules()
        self.refresh_stats()

    # ---------------------------------------------------------
    # Rule actions
    # ---------------------------------------------------------

    def toggle_applied(self, key):
        if key not in self.rules:
            return

        rule = self.rules[key]

        if rule["applied"]:
            # Clicking again allows correction.
            rule["applied"] = False
            rule["applied_at"] = None

            timestamp = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )

            self.log_change(
                rule["name"],
                False,
                timestamp
            )

        else:
            timestamp = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )

            rule["applied"] = True
            rule["applied_at"] = timestamp

            self.log_change(
                rule["name"],
                True,
                timestamp
            )

        self.save_state()
        self.refresh_stats()
        self.render_rules()

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------

    def render_rules(self):
        for widget in self.rules_frame.winfo_children():
            widget.destroy()

        if not self.rules:
            ttk.Label(
                self.rules_frame,
                text="Scan a folder to load rules.",
                padding=20
            ).pack()

            return

        # Sort: unapplied first, applied afterwards.
        sorted_rules = sorted(
            self.rules.items(),
            key=lambda item: (
                item[1]["applied"],
                item[1]["name"].lower()
            )
        )

        for index, (key, rule) in enumerate(sorted_rules):

            row = ttk.Frame(
                self.rules_frame,
                padding=(8, 6)
            )
            row.pack(
                fill="x",
                expand=True
            )

            status = "✓" if rule["applied"] else "○"

            status_label = ttk.Label(
                row,
                text=status,
                width=3,
                font=("Segoe UI", 12, "bold")
            )
            status_label.pack(side="left")

            name_frame = ttk.Frame(row)
            name_frame.pack(
                side="left",
                fill="x",
                expand=True
            )

            name_label = ttk.Label(
                name_frame,
                text=rule["name"],
                font=("Segoe UI", 10)
            )
            name_label.pack(
                anchor="w"
            )

            if rule["applied_at"]:
                ttk.Label(
                    name_frame,
                    text=f"Applied: {rule['applied_at']}",
                    font=("Segoe UI", 8)
                ).pack(anchor="w")

            button_text = (
                "Applied ✓"
                if rule["applied"]
                else "Applied"
            )

            button = ttk.Button(
                row,
                text=button_text,
                command=lambda k=key: self.toggle_applied(k)
            )
            button.pack(
                side="right",
                padx=5
            )

            ttk.Separator(
                self.rules_frame,
                orient="horizontal"
            ).pack(
                fill="x"
            )

    def refresh_stats(self):
        total = len(self.rules)
        applied = sum(
            1 for rule in self.rules.values()
            if rule["applied"]
        )
        remaining = total - applied

        self.stats_label.config(
            text=(
                f"{applied} applied, "
                f"{remaining} to go"
            )
        )

    # ---------------------------------------------------------
    # Utility buttons
    # ---------------------------------------------------------

    def open_log(self):
        if not LOG_FILE.exists():
            LOG_FILE.touch()

        try:
            import os
            os.startfile(LOG_FILE)
        except Exception as e:
            messagebox.showerror(
                "Open log",
                f"Could not open log:\n{e}"
            )

    def reset_status(self):
        if not self.rules:
            return

        answer = messagebox.askyesno(
            "Reset",
            "Reset Applied status for all rules?"
        )

        if not answer:
            return

        timestamp = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        for rule in self.rules.values():
            if rule["applied"]:
                self.log_change(
                    rule["name"],
                    False,
                    timestamp
                )

            rule["applied"] = False
            rule["applied_at"] = None

        self.save_state()
        self.refresh_stats()
        self.render_rules()


def main():
    root = tk.Tk()
    app = RuleTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
