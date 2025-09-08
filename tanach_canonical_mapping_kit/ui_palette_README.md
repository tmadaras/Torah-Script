
# Color Palette QA

- Apply variables from `ui_palette.css` throughout; avoid hard-coded colors.
- Verify contrast with Lighthouse; remediate any Accessibility warnings.
- Prefer readable dark surfaces (`--color-surface`) over pure black; text should use `--color-text`.
- Token hover/focus should be accessible: `--color-accent` outline and `--color-highlight` background if needed.
