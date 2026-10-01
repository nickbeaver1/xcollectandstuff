from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(r"C:\Users\n.perepelitsa\Desktop\Domains left to check_cleaned.txt")

OUTPUT_DIR = INPUT_FILE.parent / "parts"

TARGET_LINES = 200


# ============================================================
# READ FILE
# ============================================================

if not INPUT_FILE.exists():
    print(f"ERROR: File not found:")
    print(INPUT_FILE)
    raise SystemExit(1)

print(f"Input file: {INPUT_FILE}")

with INPUT_FILE.open("r", encoding="utf-8-sig") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")


# ============================================================
# PARSE RULES
#
# Every line starting with # begins a new rule.
# Everything until the next # belongs to that rule.
# ============================================================

rules = []
current_rule = []

for line in lines:

    # New rule starts with #
    if line.startswith("#"):

        # Save previous rule
        if current_rule:
            rules.append(current_rule)

        # Start new rule
        current_rule = [line]

    else:
        # Continue current rule
        current_rule.append(line)


# Save final rule
if current_rule:
    rules.append(current_rule)


print(f"Rules found: {len(rules)}")


# ============================================================
# CHECK FOR DATA BEFORE FIRST #
# ============================================================

if lines and not lines[0].startswith("#"):
    preamble = []

    for line in lines:
        if line.startswith("#"):
            break
        preamble.append(line)

    if preamble:
        print(
            f"WARNING: {len(preamble)} lines appear before the first # rule."
        )


# ============================================================
# PREPARE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(exist_ok=True)

# Remove old generated parts
for old_file in OUTPUT_DIR.glob("part_*.txt"):
    old_file.unlink()


# ============================================================
# SPLIT INTO PARTS
#
# We aim for ~200 lines.
# We NEVER split a rule.
# ============================================================

parts = []
current_part = []
current_size = 0

for rule in rules:

    rule_size = len(rule)

    # --------------------------------------------------------
    # If adding this rule would exceed the target,
    # finish the current part first.
    # --------------------------------------------------------

    if current_part and current_size + rule_size > TARGET_LINES:

        parts.append(current_part)

        current_part = []
        current_size = 0

    # --------------------------------------------------------
    # Add the complete rule.
    # --------------------------------------------------------

    current_part.extend(rule)
    current_size += rule_size


# Save final part
if current_part:
    parts.append(current_part)


# ============================================================
# WRITE FILES
# ============================================================

for index, part in enumerate(parts, start=1):

    output_file = OUTPUT_DIR / f"part_{index:03d}.txt"

    with output_file.open("w", encoding="utf-8") as f:
        f.writelines(part)

    print(
        f"Created {output_file.name}: "
        f"{len(part)} lines / "
        f"{sum(1 for line in part if line.startswith('#'))} rules"
    )


# ============================================================
# FINAL STATISTICS
# ============================================================

total_output_lines = sum(len(part) for part in parts)

print()
print("=" * 60)
print("DONE")
print("=" * 60)

print(f"Input lines:       {len(lines)}")
print(f"Rules:             {len(rules)}")
print(f"Output parts:      {len(parts)}")
print(f"Output lines:      {total_output_lines}")
print(f"Target per part:   {TARGET_LINES}")
print(f"Output directory:  {OUTPUT_DIR}")

print()
print("IMPORTANT:")
print("- Rules were never split between files.")
print("- Original file was NOT modified.")