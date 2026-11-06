# Security Model

ContextPack is designed to create useful AI context while reducing accidental exposure of risky files.

## What ContextPack Does

- Skips risky filenames such as `.env`, private keys, and credential files
- Skips binary files
- Skips common dependency and build folders
- Redacts common secret-like values in included files
- Runs locally and offline
- Does not execute scanned project code

## What ContextPack Does Not Guarantee

ContextPack cannot guarantee that every secret is detected. Always review generated files before sharing them.

## Recommended Workflow

1. Run `contextpack build .`
2. Open `CONTEXT.md`
3. Search for sensitive terms such as `token`, `secret`, `password`, `key`
4. Remove anything private before sharing
