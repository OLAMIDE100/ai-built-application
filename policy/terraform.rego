package terraform.security

############################
# Required labels
############################

required_labels = {"solution"}

deny contains msg if {
  resource := input.resource_changes[_]
  required_label := required_labels[_]
  # Check directly if labels is null
  resource.change.after.labels == null
  msg := sprintf("Resource %s is missing required label: %s (labels is null)", [resource.address, required_label])
}

deny contains msg if {
  resource := input.resource_changes[_]
  required_label := required_labels[_]
  # Check if labels exists but doesn't contain the required label
  resource.change.after.labels != null
  not resource.change.after.labels[required_label]
  msg := sprintf("Resource %s is missing required label: %s", [resource.address, required_label])
}

