# Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for semantic versioning. The GitHub Actions workflow automatically determines version bumps based on your commit messages.

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

- **feat**: A new feature (triggers minor version bump)
- **fix**: A bug fix (triggers patch version bump)
- **docs**: Documentation only changes (triggers patch version bump)
- **style**: Changes that do not affect the meaning of the code (triggers patch version bump)
- **refactor**: A code change that neither fixes a bug nor adds a feature (triggers patch version bump)
- **perf**: A code change that improves performance (triggers patch version bump)
- **test**: Adding missing tests or correcting existing tests (triggers patch version bump)
- **chore**: Changes to the build process or auxiliary tools (triggers patch version bump)

## Breaking Changes

To trigger a major version bump, include `BREAKING CHANGE:` in the commit body or footer:

```
feat: add new API endpoint

BREAKING CHANGE: The old API endpoint has been removed
```

Or use the `!:` syntax in the type:

```
feat!: remove deprecated API endpoint
```

## Examples

### Minor Version Bump (New Feature)
```bash
git commit -m "feat: add __slots__ explanation section"
```

### Patch Version Bump (Bug Fix)
```bash
git commit -m "fix: correct undefined 'data' variable in README example"
```

### Major Version Bump (Breaking Change)
```bash
git commit -m "feat!: restructure entire documentation format

BREAKING CHANGE: All existing links and references have changed"
```

### Documentation Update
```bash
git commit -m "docs: add commit convention guide"
```

## How Versioning Works

The GitHub Actions workflow:

1. **Checks for tags**: If you push a tag like `v1.2.3`, it uses that version
2. **Analyzes commit messages**: Looks for semantic keywords since the last tag
3. **Determines version bump**:
   - `BREAKING CHANGE` or `!:` → Major version bump
   - `feat:` → Minor version bump  
   - Everything else → Patch version bump

## Manual Version Override

You can manually trigger a build with a specific version:

1. Go to Actions tab in GitHub
2. Select "Build PDF Documentation"
3. Click "Run workflow"
4. Enter your desired version (e.g., "1.0.0")

## PDF Output

The workflow generates:
- **Filename**: `Mastering-New-Python-Libraries-v<version>.pdf`
- **Features**: Table of contents, syntax highlighting, professional formatting
- **Artifact**: Available for 90 days in GitHub Actions
- **Release**: Automatically attached to GitHub releases when you tag 
