File: steps-to-fix.md

# Steps to Remove Only the Second Resource

## Requirement

The current Terraform configuration uses the `count` meta-argument to create five local files.

Current resources:

local_file.foo[0]
local_file.foo[1]
local_file.foo[2]
local_file.foo[3]
local_file.foo[4]

The requirement is to remove only the second resource (local_file.foo[1]) without recreating the remaining resources. After the changes, running `terraform plan` should display:

No changes.
Infrastructure matches the configuration.

---

## Problem

The current configuration uses the `count` meta-argument.

With `count`, Terraform identifies resources using numeric indexes.

If one resource is removed from the middle, the indexes of the remaining resources shift. Terraform interprets this as multiple resources changing, which can lead to unnecessary recreation of resources.

---

## Solution

### Step 1: Update the Terraform configuration

Convert the resource from `count` to `for_each`.

Current configuration:

```hcl
resource "local_file" "foo" {
  count = var.files

  filename = "file${count.index}.txt"
  content  = "# Some content for file ${count.index}"
}
```

Updated configuration:

```hcl
resource "local_file" "foo" {

  for_each = {
    "0" = {}
    "1" = {}
    "2" = {}
    "3" = {}
    "4" = {}
  }

  filename = "file${each.key}.txt"
  content  = "# Some content for file ${each.key}"
}
```

---

### Step 2: Move the Terraform state

Do not edit the `terraform.tfstate` file manually.

Move the existing state using the following commands:

```bash
terraform state mv local_file.foo[0] local_file.foo["0"]
terraform state mv local_file.foo[1] local_file.foo["1"]
terraform state mv local_file.foo[2] local_file.foo["2"]
terraform state mv local_file.foo[3] local_file.foo["3"]
terraform state mv local_file.foo[4] local_file.foo["4"]
```

This updates the resource addresses in the Terraform state without recreating any resources.

---

### Step 3: Remove the second resource

Delete only key `"1"` from the `for_each` map.

Updated `for_each`:

```hcl
for_each = {
  "0" = {}
  "2" = {}
  "3" = {}
  "4" = {}
}
```

Terraform will now identify only `local_file.foo["1"]` as the resource to remove.

---

### Step 4: Verify the execution plan

Run:

```bash
terraform plan
```

Expected result:

Only `local_file.foo["1"]` is marked for destruction.

No other resources should be recreated or modified.

---

### Step 5: Apply the changes

Run:

```bash
terraform apply
```

Terraform removes only the second resource.

---

### Step 6: Verify the final state

Run:

```bash
terraform plan
```

Expected output:

```
No changes.
Infrastructure matches the configuration.
```

This confirms that only the required resource was removed and all remaining resources were preserved.