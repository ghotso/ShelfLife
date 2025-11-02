# Contributing to ShelfLife

Thank you for your interest in contributing to ShelfLife! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Documentation](#documentation)
- [Internationalization](#internationalization)

## Code of Conduct

By participating in this project, you agree to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Be open to different perspectives

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- Git installed
- Python 3.11 or 3.12
- Node.js 18+
- Docker (optional, for testing)
- A code editor (VS Code recommended)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ShelfLife.git
   cd ShelfLife
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/ShelfLife.git
   ```

## Development Setup

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The backend will start on `http://localhost:8000`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:3000`.

### Database Setup

The SQLite database is automatically created on first run in the `data/` directory. You can reset it by deleting `data/shelflife.db`.

## Making Changes

### Workflow

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes:**
   - Write clear, readable code
   - Follow the coding standards (see below)
   - Add tests if applicable
   - Update documentation

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Test additions/changes
   - `chore:` - Maintenance tasks

4. **Keep your branch updated:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request:**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Submit the PR

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Maximum line length: 100 characters
- Use meaningful variable and function names

**Example:**
```python
def get_movie_data(movie: Any) -> Dict[str, Any]:
    """Extract movie data for rule evaluation.
    
    Args:
        movie: Plex movie object
        
    Returns:
        Dictionary containing movie data fields
    """
    return {
        "key": movie.key,
        "title": movie.title,
        ...
    }
```

### TypeScript/React (Frontend)

- Follow React best practices
- Use functional components with hooks
- Use TypeScript for type safety
- Use meaningful component and variable names
- Format with Prettier (configured in project)

**Example:**
```typescript
interface RuleBuilderProps {
  libraries: Library[]
  rule?: Rule
  onClose: () => void
  onSave: () => void
}

export default function RuleBuilder({ libraries, rule, onClose, onSave }: RuleBuilderProps) {
  // Component implementation
}
```

### General Guidelines

- **Keep functions small and focused** - One responsibility per function
- **Write self-documenting code** - Code should explain itself
- **Comment complex logic** - Explain why, not what
- **Avoid deep nesting** - Use early returns and guard clauses
- **Handle errors gracefully** - Always provide meaningful error messages

## Testing

### Manual Testing

Before submitting a PR, please test your changes:

1. **Test the feature** - Use the UI to verify functionality
2. **Test edge cases** - Try unusual inputs or conditions
3. **Test error handling** - Verify error messages are clear
4. **Test with different data** - Try with empty/null data

### Automated Testing

While automated tests are not yet fully implemented, we're working on it. When adding new features:

- Consider how it could be tested
- Document test scenarios in your PR
- Future: Add unit tests for critical functions

### Testing Checklist

- [ ] Feature works as expected
- [ ] Edge cases handled
- [ ] Error messages are clear
- [ ] UI is responsive
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Documentation updated

## Submitting Changes

### Pull Request Template

When creating a PR, include:

1. **Description:**
   - What changes were made
   - Why they were made
   - How to test them

2. **Screenshots:**
   - If UI changes, include before/after screenshots
   - Show the feature in action

3. **Checklist:**
   - Code follows style guidelines
   - Documentation updated
   - Tests pass (when applicable)
   - No breaking changes (or documented if intentional)

### PR Review Process

1. **Initial Review:**
   - Maintainers will review your PR
   - Automated checks may run (if configured)

2. **Feedback:**
   - Address any review comments
   - Make requested changes
   - Push updates to your branch

3. **Approval:**
   - Once approved, PR will be merged
   - Your contributions will be credited

## Documentation

### Code Documentation

- **Docstrings:** Add docstrings to functions and classes
- **Comments:** Explain complex logic
- **Type hints:** Use type hints in Python

### User Documentation

When adding features:

1. **Update User Guide:** Document new features in `docs/USER_GUIDE.md`
2. **Update API Docs:** If API changed, update `docs/API.md`
3. **Add Screenshots:** Add screenshot placeholders where helpful
4. **Update README:** If major feature, update main README

### Documentation Format

- Use Markdown
- Follow existing structure
- Include code examples
- Add screenshot placeholders: `![Description](./screenshots/filename.png)`

## Project Structure

```
ShelfLife/
├── backend/
│   ├── app/
│   │   ├── integrations/    # Plex, Radarr, Sonarr integrations
│   │   ├── routers/         # API endpoints
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── rule_engine.py   # Rule evaluation logic
│   └── main.py              # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── lib/             # Utilities and API client
│   │   └── i18n/            # Internationalization
│   └── public/              # Static assets
├── docs/                    # Documentation
└── data/                    # SQLite database (gitignored)
```

## Areas for Contribution

We welcome contributions in these areas:

### Features

- Additional rule conditions
- New action types
- UI improvements
- Performance optimizations
- Better error handling

### Documentation

- User guide improvements
- API documentation enhancements
- Code examples
- Tutorials and guides

### Bug Fixes

- Report bugs via GitHub Issues
- Fix bugs and submit PRs
- Improve error messages

### Testing

- Add unit tests
- Add integration tests
- Improve test coverage

### Internationalization

Adding translations is a great way to contribute! See the [Translations Guide](TRANSLATIONS.md) for detailed step-by-step instructions.

- Add new languages
- Improve existing translations
- Fix translation issues
- Report missing translations

## Getting Help

- **Questions?** Open a GitHub Discussion
- **Found a bug?** Open a GitHub Issue
- **Need help?** Ask in Discussions or check existing Issues

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md (if we create one)
- Credited in release notes
- Thanked in PRs and Issues

Thank you for contributing to ShelfLife! 🎉

---

*Documentation version: 1.0 | Last updated: 02.11.2025*

