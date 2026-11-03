# Token Budgeting

ContextPack estimates token usage so you can keep generated context manageable.

## Basic check

```bash
contextpack tokens .
```

## Detailed budget report

```bash
contextpack budget . --output context-budget.md
```

## Reduce token size

- Use `--profile compact`
- Use `--max-files`
- Add generated folders to `ignore_dirs`
- Use `split` for large repositories
- Exclude large extensions with `exclude_extensions`
