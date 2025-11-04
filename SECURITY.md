# Security Policy

## Supported Versions

We actively support the following versions of ShelfLife with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of ShelfLife seriously. If you discover a security vulnerability, please follow these steps:

### 1. **Do Not** disclose the vulnerability publicly

Please do not create a public GitHub issue or discuss the vulnerability in public forums until we have addressed it.

### 2. Report the vulnerability

Email security details to: **[your-email@example.com]** (replace with your security contact email)

Or create a **private security advisory** on GitHub:
- Go to the repository's Security tab
- Click "Report a vulnerability"
- Fill out the security advisory form

### 3. What to include in your report

Please provide as much information as possible:

- **Type of vulnerability** (e.g., path traversal, authentication bypass, SQL injection)
- **Affected component** (e.g., API endpoint, frontend component, database)
- **Steps to reproduce** the vulnerability
- **Potential impact** (e.g., data exposure, unauthorized access, denial of service)
- **Suggested fix** (if you have one)
- **Proof of concept** (if applicable, but be careful not to include malicious code)

### 4. Response timeline

We will acknowledge receipt of your report within **48 hours** and aim to provide an initial assessment within **7 days**. We will keep you informed of our progress throughout the process.

### 5. Disclosure policy

- We will work with you to understand and resolve the issue quickly
- We will notify you when the vulnerability is fixed
- We will credit you (if desired) for discovering the vulnerability
- We will publish a security advisory after the fix is released

## Security Best Practices

### For Users

When using ShelfLife, please follow these security best practices:

1. **Keep ShelfLife updated** - Always use the latest supported version
2. **Secure your API tokens** - Never share your Plex, Radarr, or Sonarr API tokens
3. **Use HTTPS** - If exposing ShelfLife over the internet, use HTTPS with a valid certificate
4. **Network security** - Consider running ShelfLife behind a firewall or VPN
5. **Database security** - Protect your SQLite database file (`data/shelflife.db`) with appropriate file permissions
6. **Regular backups** - Backup your database regularly to prevent data loss

### For Developers

- **Input validation** - All user input is validated and sanitized
- **Path traversal protection** - File path sanitization is implemented to prevent directory traversal attacks
- **Credential encryption** - API tokens and credentials are encrypted at rest using cryptography
- **CORS configuration** - CORS is configured appropriately for production use
- **SQL injection prevention** - SQLAlchemy ORM is used to prevent SQL injection
- **Dependency management** - Dependencies are kept up to date; check for security advisories regularly

## Known Security Considerations

### Plex API Token Security

ShelfLife stores Plex API tokens in an encrypted format. However, if an attacker gains access to your database file and the encryption key (stored in the application), they could decrypt these tokens. Ensure your database file has appropriate file system permissions.

### Network Exposure

By default, ShelfLife binds to `0.0.0.0:8000`, making it accessible on all network interfaces. For production use:
- Use a reverse proxy (nginx, Traefik, etc.) with HTTPS
- Consider using Docker networking to isolate the container
- Use firewall rules to restrict access

### Self-Hosted Nature

ShelfLife is designed for self-hosting. Users are responsible for:
- Securing their hosting environment
- Managing updates and patches
- Configuring network security
- Protecting their database and credentials

## Security Updates

Security updates will be released as patch versions (e.g., 3.0.1, 3.0.2) for the current major version. Critical security vulnerabilities will be patched as quickly as possible.

## Credits

We would like to thank all security researchers who responsibly disclose vulnerabilities and help make ShelfLife more secure.

