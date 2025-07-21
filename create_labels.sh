#!/bin/bash

# Script to create GitHub labels for conventional commit types

REPO="brunseba/tools-vmware-vra-cli"

# Array of labels to be created
LABELS=(
  "type: feat:New features:0052cc"
  "type: fix:Bug fixes:d73a4a"
  "type: docs:Documentation changes:0075ca"
  "type: style:Code style changes:ffd700"
  "type: refactor:Code refactoring:fbca04"
  "type: test:Adding or updating tests:28a745"
  "type: chore:Build process or auxiliary tool changes:6f42c1"
  "type: perf:Performance improvements:ff6b6b"
  "type: ci:Continuous integration changes:2cbe4e"
  "priority: high:High priority:e11d21"
  "priority: medium:Medium priority:ff9500"
  "priority: low:Low priority:0e8a16"
  "status: needs-triage:Needs initial review and categorization:fbca04"
  "status: accepted:Accepted for implementation:0052cc"
  "status: in-progress:Currently being worked on:0e8a16"
  "status: blocked:Blocked by dependencies or external factors:e11d21"
  "good-first-issue:Good for newcomers to the project:7057ff"
  "help-wanted:Extra attention is needed:128a0c"
)

# Function to create a label
create_label() {
  IFS=":" read -r NAME DESCRIPTION COLOR <<< "$1"
  gh label create "$NAME" --description "$DESCRIPTION" --color "$COLOR" --repo "$REPO"
}

# Iterate over the labels and create each one
for LABEL in "${LABELS[@]}"; do
  create_label "$LABEL"
done

