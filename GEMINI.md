# Disease Prediction Assistant

## Project Overview

This project is a production-quality Streamlit-based Disease Prediction Assistant.

The objective is to build clean, maintainable, reliable software while preserving the existing architecture and user experience.

---

# Global Engineering Philosophy

Always think before coding.

Never immediately generate code.

Internally perform the following steps:

1. Understand the request.
2. Inspect the relevant files.
3. Understand the existing architecture.
4. Find the root cause.
5. Reuse existing code.
6. Consider simpler alternatives.
7. Implement only the minimum required solution.

---

# Coding Principles

Prefer

- modifying existing files
- existing utilities
- existing components
- Python standard library
- Streamlit built-in functionality

Avoid

- duplicate code
- wrappers
- unnecessary helper functions
- unnecessary abstraction
- unnecessary classes
- overengineering
- premature optimization

---

# File Policy

Only create new files when absolutely necessary.

Prefer editing existing files.

Never create utility files that are used only once.

---

# Architecture

Respect the current folder structure.

Preserve project architecture.

Never redesign unless explicitly requested.

Never rename files without reason.

Never move files unnecessarily.

---

# Streamlit Guidelines

Preserve

- session_state
- caching
- navigation
- responsiveness
- styling
- layout
- theme

Avoid unnecessary reruns.

Use cache_resource and cache_data appropriately.

---

# Machine Learning

Never retrain models unless requested.

Separate preprocessing from prediction.

Reuse trained models.

Validate model inputs.

Handle invalid user input gracefully.

---

# UI Guidelines

Maintain

- spacing
- typography
- responsiveness
- accessibility
- existing design language

Never redesign UI unless requested.

---

# Performance

Avoid

- repeated model loading
- repeated database queries
- repeated file reads
- unnecessary loops

---

# Error Handling

Handle expected errors.

Show user-friendly messages.

Never silently ignore exceptions.

---

# Review Checklist

Before completing any task verify:

✓ Root cause solved

✓ Minimal code changes

✓ No duplicated logic

✓ No unnecessary abstractions

✓ Existing architecture preserved

✓ Existing UI preserved

✓ No regressions introduced

---

# Response Format

Always respond using

## Analysis

## Plan

## Implementation

## Verification

---

# Never

Never overengineer.

Never future-proof unnecessarily.

Never rewrite working code.

Never create unnecessary files.

Never modify unrelated code.

---

# Always

Keep diffs small.

Write production-quality code.

Prefer readability.

Prefer simplicity.

Preserve existing architecture.