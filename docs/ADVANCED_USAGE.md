# Advanced Usage

This guide covers the commands that are useful for larger repositories and deeper AI workflows.

## Create a full artifact pack

```bash
contextpack pack . --output-dir contextpack-artifacts --zip contextpack-artifacts.zip
```

This creates the main context bundle, manifest, outline, index, insights, and audit report.

## Review token budget

```bash
contextpack budget . --profile deep --output context-budget.md
```

Use this before sending context to tools with strict context windows.

## Generate an outline

```bash
contextpack outline . --output context-outline.md
```

The outline extracts classes, functions, headings, and important symbols from selected files.

## Audit context safety

```bash
contextpack audit . --output context-audit.md
```

Use this command before sharing generated context externally.
