import json
import sys

# Read tfplan.json
with open(sys.argv[1], "r") as file:
    plan = json.load(file)

safe = True

# No resource changes
if "resource_changes" not in plan:
    print("No resource changes found.")
    sys.exit(0)

for resource in plan["resource_changes"]:

    name = resource["address"]
    change = resource["change"]
    action = change["actions"]

    # Ignore no-op
    if action == ["no-op"]:
        continue

    # CREATE
    if action == ["create"]:
        print(f"[PASS] {name} -> Create")
        continue

    # DESTROY / REPLACE
    if "delete" in action:
        print(f"[FAIL] {name} -> Destroy or Replace detected")
        safe = False
        continue

    # UPDATE
    if action == ["update"]:

        before = change.get("before", {}) or {}
        after = change.get("after", {}) or {}

        changed_fields = []

        # Find changed top-level fields
        for key in set(before.keys()) | set(after.keys()):
            if before.get(key) != after.get(key):
                changed_fields.append(key)

        # Only tags can change
        if changed_fields != ["tags"]:
            print(f"[FAIL] {name} -> Changed fields: {changed_fields}")
            safe = False
            continue

        # Compare tags
        before_tags = before.get("tags", {}) or {}
        after_tags = after.get("tags", {}) or {}

        changed_tags = []

        for tag in set(before_tags.keys()) | set(after_tags.keys()):
            if before_tags.get(tag) != after_tags.get(tag):
                changed_tags.append(tag)

        # Only GitCommitHash is allowed
        if changed_tags == ["GitCommitHash"]:
            print(f"[PASS] {name} -> Only GitCommitHash changed")
        else:
            print(f"[FAIL] {name} -> Tag changes: {changed_tags}")
            safe = False

print("\n------------------------")

if safe:
    print("Terraform plan is SAFE to apply")
else:
    print("Terraform plan is NOT SAFE to apply")