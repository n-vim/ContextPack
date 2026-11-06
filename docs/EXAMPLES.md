# Examples

## Create a Review Bundle

```bash
contextpack build . --prompt review --output CONTEXT.md
```

## Create a Bugfix Bundle

```bash
contextpack build . --prompt bugfix --output BUG_CONTEXT.md
```

## Limit Included Files

```bash
contextpack build . --max-files 25
```

## Generate a JSON Report

```bash
contextpack export . --format json --output context-report.json
```

## Inspect Included Files

```bash
contextpack inspect . --limit 50
```
