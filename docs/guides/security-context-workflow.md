# Security Context Workflow

Use the security profile when asking for security review:

```bash
contextpack build . --profile security --output SECURITY_CONTEXT.md
contextpack audit . --output context-audit.md
```

Review the audit before sharing the context.
