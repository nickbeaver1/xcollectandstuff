from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    r"C:\Users\n.perepelitsa\Desktop\Domains left to check.txt"
)

OUTPUT_FILE = INPUT_FILE.with_name(
    INPUT_FILE.stem + "_cleaned.txt"
)


# ============================================================
# RULE CLEANING
# ============================================================

def clean_rule(line: str) -> str:
    """
    Clean one rule.

    Rules:
    1. Lines beginning with '#' are NOT modified.
    2. Remove ';'
    3. Keep the first '*' in the line.
    4. Remove the second '*' in the line.
    5. Do NOT modify hyphens.
    """

    # Remove only the line ending
    line = line.rstrip("\r\n")

    # --------------------------------------------------------
    # IMPORTANT:
    # Comment/category lines are protected completely.
    #
    # Example:
    # # Вельская диван.txt
    #
    # stays exactly the same.
    # --------------------------------------------------------

    if line.startswith("#"):
        return line

    # --------------------------------------------------------
    # Remove semicolons
    #
    # Example:
    # *example.com/*; 1;
    #
    # ->
    # *example.com/* 1
    # --------------------------------------------------------

    line = line.replace(";", "")

    # --------------------------------------------------------
    # Keep the first '*' and remove the second '*'
    #
    # Example:
    #
    # *huggingface.co/* 1
    #               ^
    #               second *
    #
    # ->
    #
    # *huggingface.co/ 1
    # --------------------------------------------------------

    first_star = line.find("*")

    if first_star != -1:

        second_star = line.find("*", first_star + 1)

        if second_star != -1:

            line = (
                line[:second_star]
                + line[second_star + 1:]
            )

    # Remove whitespace at the beginning/end
    return line.strip()


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Check input file
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        print("[ERROR] Input file was not found:")
        print(INPUT_FILE)

        return

    print("========================================")
    print("       RULE CLEANER")
    print("========================================")
    print()

    print("[INFO] Input file:")
    print(INPUT_FILE)
    print()

    # --------------------------------------------------------
    # Read file
    # --------------------------------------------------------

    lines = INPUT_FILE.read_text(
        encoding="utf-8",
        errors="replace"
    ).splitlines()

    original_count = len(lines)

    print(f"[INFO] Read {original_count} lines.")
    print()

    # --------------------------------------------------------
    # Clean rules
    # --------------------------------------------------------

    cleaned_lines = []

    for line in lines:

        cleaned = clean_rule(line)

        cleaned_lines.append(cleaned)

    # --------------------------------------------------------
    # Remove duplicates
    #
    # dict.fromkeys() preserves the original order.
    #
    # Example:
    #
    # google.com
    # yandex.ru
    # google.com
    #
    # becomes:
    #
    # google.com
    # yandex.ru
    # --------------------------------------------------------

    unique_lines = list(
        dict.fromkeys(cleaned_lines)
    )

    duplicates_removed = (
        len(cleaned_lines)
        - len(unique_lines)
    )

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    OUTPUT_FILE.write_text(
        "\n".join(unique_lines) + "\n",
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print("========================================")
    print("              DONE")
    print("========================================")
    print()

    print(f"Original lines:      {original_count}")
    print(f"Cleaned lines:       {len(cleaned_lines)}")
    print(f"Unique lines:        {len(unique_lines)}")
    print(f"Duplicates removed:  {duplicates_removed}")

    print()
    print("[INFO] Output file:")
    print(OUTPUT_FILE)

    print()
    print("Original file was NOT modified.")


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()