import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import re


class UserGateCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("UserGate Rule Cleaner")
        self.root.geometry("1000x700")
        self.root.minsize(750, 500)

        self.file_path = None
        self.lines = []

        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")

        ttk.Button(
            top,
            text="Open TXT file",
            command=self.open_file
        ).pack(side="left")

        self.file_label = ttk.Label(
            top,
            text="No file selected"
        )
        self.file_label.pack(
            side="left",
            padx=12
        )

        # Action buttons
        actions = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        actions.pack(fill="x")

        ttk.Button(
            actions,
            text="Clear 0",
            command=lambda: self.clean_action("0")
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            actions,
            text="Clear 1",
            command=lambda: self.clean_action("1")
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="Clear whichever (0/1)",
            command=self.clean_detected
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="Copy output",
            command=self.copy_output
        ).pack(side="right")

        self.info_label = ttk.Label(
            self.root,
            text="Open a rule file first.",
            padding=(12, 5)
        )
        self.info_label.pack(fill="x")

        # Output
        output_frame = ttk.Frame(self.root, padding=12)
        output_frame.pack(fill="both", expand=True)

        self.text = tk.Text(
            output_frame,
            wrap="none",
            font=("Consolas", 10),
            undo=False
        )

        y_scroll = ttk.Scrollbar(
            output_frame,
            orient="vertical",
            command=self.text.yview
        )

        x_scroll = ttk.Scrollbar(
            output_frame,
            orient="horizontal",
            command=self.text.xview
        )

        self.text.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.text.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        y_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        x_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

    # ---------------------------------------------------------
    # File handling
    # ---------------------------------------------------------

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Select UserGate TXT rule",
            filetypes=[
                ("TXT files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return

        self.file_path = Path(path)

        try:
            self.lines = self.file_path.read_text(
                encoding="utf-8-sig"
            ).splitlines(keepends=True)

        except UnicodeDecodeError:
            try:
                self.lines = self.file_path.read_text(
                    encoding="cp1251"
                ).splitlines(keepends=True)

            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Could not read file:\n{e}"
                )
                return

        self.show_original()

    def show_original(self):
        self.text.delete("1.0", tk.END)
        self.text.insert(
            "1.0",
            "".join(self.lines)
        )

        self.update_info()

    # ---------------------------------------------------------
    # Analysis
    # ---------------------------------------------------------

    def detect_actions(self):
        has_zero = False
        has_one = False

        for raw in self.lines:
            line = raw.rstrip("\r\n")

            if not line or line.startswith("#"):
                continue

            if re.search(r"0\s*$", line):
                has_zero = True

            if re.search(r"1\s*$", line):
                has_one = True

        return has_zero, has_one

    def update_info(self):
        zero, one = self.detect_actions()

        if zero and one:
            text = "File contains BOTH 0 and 1"
        elif zero:
            text = "File contains only 0"
        elif one:
            text = "File contains only 1"
        else:
            text = "No 0/1 action values detected"

        self.info_label.config(text=text)

    # ---------------------------------------------------------
    # Cleaning
    # ---------------------------------------------------------

    def clean_action(self, action):
        if not self.lines:
            messagebox.showinfo(
                "No file",
                "Open a TXT file first."
            )
            return

        output = []

        removed = 0
        kept = 0

        for raw in self.lines:
            line = raw.rstrip("\r\n")

            # Keep rule header
            if line.startswith("#"):
                output.append(raw)
                continue

            # Keep empty lines
            if not line.strip():
                output.append(raw)
                continue

            # Remove final 0/1
            if re.search(r"[01]\s*$", line):

                cleaned = re.sub(
                    r"[01]\s*$",
                    "",
                    line
                ).rstrip()

                output.append(cleaned + "\n")

                removed += 1
                kept += 1

            else:
                # Unexpected line: leave untouched
                output.append(raw)
                kept += 1

        self.show_output(
            output,
            f"Removed action '{action}' from {removed} entries."
        )

    def clean_detected(self):
        zero, one = self.detect_actions()

        if zero and one:
            messagebox.showwarning(
                "Both 0 and 1 found",
                "This file contains BOTH 0 and 1.\n\n"
                "Choose 'Clear 0' or 'Clear 1' manually."
            )
            return

        if zero:
            self.clean_action("0")

        elif one:
            self.clean_action("1")

        else:
            messagebox.showinfo(
                "Nothing to clean",
                "No trailing 0 or 1 values were found."
            )

    # ---------------------------------------------------------
    # Output
    # ---------------------------------------------------------

    def show_output(self, output, message):
        self.text.delete("1.0", tk.END)
        self.text.insert(
            "1.0",
            "".join(output)
        )

        self.info_label.config(
            text=message
        )

    def copy_output(self):
        output = self.text.get(
            "1.0",
            tk.END
        ).rstrip("\n")

        if not output:
            messagebox.showinfo(
                "Copy",
                "There is no output to copy."
            )
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        self.root.update()

        self.info_label.config(
            text="Output copied to clipboard."
        )


def main():
    root = tk.Tk()
    UserGateCleaner(root)
    root.mainloop()


if __name__ == "__main__":
    main()
