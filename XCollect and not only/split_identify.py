from pathlib import Path
import re
import re as regex


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(r"C:\Users\n.perepelitsa\Desktop")

INPUT_DIR = BASE_DIR / "parts"

OUTPUT_DIR = BASE_DIR / "classified_rules"


# ============================================================
# CLEAN OLD OUTPUT
# ============================================================

OUTPUT_DIR.mkdir(exist_ok=True)

for old_file in OUTPUT_DIR.glob("*.txt"):
    old_file.unlink()


# ============================================================
# FIND PART FILES
# ============================================================

part_files = sorted(INPUT_DIR.glob("part_*.txt"))

if not part_files:
    print(f"ERROR: No part_*.txt files found in:")
    print(INPUT_DIR)
    raise SystemExit(1)

print(f"Found {len(part_files)} part files.")
print()


# ============================================================
# DATA STRUCTURE
#
# rules = {
#     "Rule Name": {
#         "header": "# Rule Name\n",
#         "allow": [...],
#         "block": [...],
#         "unknown": [...]
#     }
# }
# ============================================================

rules = {}

current_rule_name = None
current_rule_header = None

manual_review = []


# ============================================================
# PROCESS ALL PARTS
# ============================================================

for part_file in part_files:

    print(f"Reading: {part_file.name}")

    with part_file.open("r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    for line_number, raw_line in enumerate(lines, start=1):

        line = raw_line.rstrip("\r\n")

        # ----------------------------------------------------
        # NEW RULE
        # ----------------------------------------------------

        if line.startswith("#"):

            current_rule_header = raw_line
            current_rule_name = line[1:].strip()

            if not current_rule_name:
                current_rule_name = "Unnamed Rule"

            # Create rule if we haven't seen it before
            if current_rule_name not in rules:

                rules[current_rule_name] = {
                    "header": current_rule_header,
                    "allow": [],
                    "block": [],
                    "unknown": []
                }

            continue


        # ----------------------------------------------------
        # DATA BEFORE FIRST RULE
        # ----------------------------------------------------

        if current_rule_name is None:

            manual_review.append(
                f"[{part_file.name}:{line_number}] {raw_line}"
            )

            continue


        # ----------------------------------------------------
        # EMPTY LINE
        # ----------------------------------------------------

        if not line.strip():
            continue


        # ----------------------------------------------------
        # DETERMINE ACTION
        #
        # Expected:
        #
        # *domain.ru/* 1
        # *domain.ru/* 0
        #
        # We only care about the FINAL 0/1.
        # ----------------------------------------------------

        match = re.search(r"([01])\s*$", line)

        if not match:

            rules[current_rule_name]["unknown"].append(raw_line)

            continue


        action = match.group(1)


        # ----------------------------------------------------
        # SAVE TO ALLOW / BLOCK
        # ----------------------------------------------------

        if action == "1":

            rules[current_rule_name]["allow"].append(raw_line)

        elif action == "0":

            rules[current_rule_name]["block"].append(raw_line)


# ============================================================
# SANITIZE WINDOWS FILE NAME
# ============================================================

def safe_filename(name):

    # Windows forbidden characters:
    # < > : " / \ | ? *

    name = re.sub(r'[<>:"/\\|?*]', '_', name)

    # Remove trailing dots/spaces
    name = name.rstrip(" .")

    # Windows reserved names
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
        "LPT6", "LPT7", "LPT8", "LPT9"
    }

    if name.upper() in reserved:
        name = "_" + name

    if not name:
        name = "Unnamed Rule"

    return name


# ============================================================
# WRITE CLASSIFIED RULES
# ============================================================

created_files = []

total_allow = 0
total_block = 0
total_unknown = 0

print()
print("=" * 70)
print("CLASSIFYING RULES")
print("=" * 70)
print()


for rule_name, data in rules.items():

    allow = data["allow"]
    block = data["block"]
    unknown = data["unknown"]

    total_allow += len(allow)
    total_block += len(block)
    total_unknown += len(unknown)

    safe_name = safe_filename(rule_name)

    # --------------------------------------------------------
    # ONLY ALLOW
    # --------------------------------------------------------

    if allow and not block:

        output_file = OUTPUT_DIR / f"{safe_name}.txt"

        with output_file.open("w", encoding="utf-8") as f:

            f.write(data["header"])
            f.writelines(allow)

        created_files.append(output_file)

        print(
            f"[ALLOW] {rule_name}: "
            f"{len(allow)} lines -> {output_file.name}"
        )


    # --------------------------------------------------------
    # ONLY BLOCK
    # --------------------------------------------------------

    elif block and not allow:

        output_file = OUTPUT_DIR / f"{safe_name}.txt"

        with output_file.open("w", encoding="utf-8") as f:

            f.write(data["header"])
            f.writelines(block)

        created_files.append(output_file)

        print(
            f"[BLOCK] {rule_name}: "
            f"{len(block)} lines -> {output_file.name}"
        )


    # --------------------------------------------------------
    # BOTH ALLOW AND BLOCK
    # --------------------------------------------------------

    elif allow and block:

        allow_file = OUTPUT_DIR / f"{safe_name}_allow.txt"
        block_file = OUTPUT_DIR / f"{safe_name}_block.txt"

        with allow_file.open("w", encoding="utf-8") as f:

            f.write(data["header"])
            f.writelines(allow)

        with block_file.open("w", encoding="utf-8") as f:

            f.write(data["header"])
            f.writelines(block)

        created_files.append(allow_file)
        created_files.append(block_file)

        print(
            f"[MIXED] {rule_name}: "
            f"{len(allow)} ALLOW + "
            f"{len(block)} BLOCK"
        )

        print(f"        -> {allow_file.name}")
        print(f"        -> {block_file.name}")


    # --------------------------------------------------------
    # EMPTY / WEIRD RULE
    # --------------------------------------------------------

    else:

        print(
            f"[EMPTY/UNKNOWN] {rule_name}: "
            f"{len(unknown)} unclassified lines"
        )


# ============================================================
# MANUAL REVIEW FILE
# ============================================================

manual_review_file = OUTPUT_DIR / "MANUAL_REVIEW.txt"

with manual_review_file.open("w", encoding="utf-8") as f:

    f.write("# Lines requiring manual review\n\n")

    for rule_name, data in rules.items():

        if not data["unknown"]:
            continue

        f.write("=" * 70 + "\n")
        f.write(f"# {rule_name}\n")
        f.write("=" * 70 + "\n")

        f.writelines(data["unknown"])
        f.write("\n")


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("DONE")
print("=" * 70)

print(f"Rules found:             {len(rules)}")
print(f"ALLOW entries:           {total_allow}")
print(f"BLOCK entries:           {total_block}")
print(f"Manual-review entries:   {total_unknown}")
print(f"Output files:            {len(created_files)}")
print()
print(f"Output directory:")
print(OUTPUT_DIR)

if total_unknown:
    print()
    print("WARNING:")
    print(
        f"{total_unknown} lines could not be classified "
        f"as 0 or 1."
    )
    print(f"Check: {manual_review_file}")

print()
print("Original parts were NOT modified.")