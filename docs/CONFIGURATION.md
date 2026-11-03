# Configuration

ContextPack uses `.contextpack.yaml` for project-specific settings.

Create the config file:

```bash
contextpack init .
```

## Options

| Key | Purpose |
| --- | --- |
| `max_file_size_kb` | Skip files larger than this size |
| `token_budget` | Soft token budget for the bundle |
| `include_hidden_files` | Include hidden files and folders |
| `include_tests` | Include test files |
| `include_docs` | Include docs files |
| `include_config` | Include config files |
| `include_gitignored` | Reserved for future gitignore integration |
| `redact_secrets` | Mask common secret-like values |
| `output_file` | Default bundle output path |
| `ignore_dirs` | Directories to skip |
| `ignore_files` | Files to skip |
| `include_extensions` | Only include these extensions when set |
| `exclude_extensions` | Always exclude these extensions |
