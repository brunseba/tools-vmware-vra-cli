# Changelog

All notable changes to VMware vRA CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2025-01-21

### Added
- Added --version option to CLI for better version management
- Cross-platform installation scripts for development tools
- Comprehensive GitHub workflow for multiarch wheel building and publishing
- Comprehensive tag management functionality
- Taskfile for task automation
- MIT license for open source distribution

### Changed
- Refined GitHub workflow configuration for better reliability
- Updated README with correct repository URLs and tag management commands
- Removed Windows targets from workflow to reduce build complexity

### Fixed
- Improved CI/CD pipeline stability

## [0.4.0] - 2025-01-21

### Added
- Initial release of VMware vRA CLI
- Service Catalog integration with vRealize Orchestrator API
- Authentication management with secure token storage
- Catalog item listing, viewing, and requesting
- Deployment management (list, show, delete, resources)
- Workflow operations (list, run, monitor)
- Multiple output formats (table, JSON, YAML)
- Configuration management with profiles
- Rich terminal output with colors and progress indicators
- Comprehensive documentation with MkDocs
- Support for environment variables and configuration files
- SSL/TLS configuration options
- Batch operations support
- Interactive and non-interactive modes

### Security
- Secure credential storage using system keyring
- Bearer token authentication
- SSL certificate verification
- Environment variable support for CI/CD

## [0.1.0] - 2024-07-21

### Added
- Initial project structure
- Basic CLI framework with Click
- Authentication commands
- Service Catalog API client
- Deployment operations
- Workflow execution capabilities
- Documentation structure
- Development tooling setup

### Changed
- N/A (Initial release)

### Deprecated
- N/A (Initial release)

### Removed
- N/A (Initial release)

### Fixed
- N/A (Initial release)

### Security
- Implemented secure token storage
- Added SSL verification

## Contributing

When contributing to this project, please:

1. Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages
2. Update this changelog with your changes
3. Include appropriate version bumps
4. Add relevant documentation updates

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Examples:
```
feat(catalog): add support for catalog item schema retrieval

fix(auth): resolve token storage issue on macOS

docs(api): update authentication examples

chore(deps): update pydantic to v2.5.0
```
