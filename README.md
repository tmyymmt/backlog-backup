# Backlog Backup

A command-line tool for backing up Backlog project data.

[日本語のREADME](README_ja.md)

## Features

- Backup Backlog project data from the command line
- Back up multiple types of project data:
  - Issues (list and details)
  - Wiki pages
  - Files
  - Git repositories
  - Subversion repositories
- Uses Backlog API where possible
- Falls back to web scraping when necessary (with proper rate limiting)

## Installation

### Requirements

- Python 3.8 or higher
- Git (for Git repository backup)
- Subversion (for SVN repository backup)

### Install from source

```bash
# Clone the repository
git clone https://github.com/tmyymmt/backlog-backup.git
cd backlog-backup

# Install the package
pip install -e .

# For web scraping support (optional)
pip install -e ".[scraping]"
```

### Using standalone executable

Standalone executables are available for Windows, macOS, and Linux platforms. These executables do not require a separate Python installation.

#### Download

Download the appropriate executable for your platform from the [releases page](https://github.com/tmyymmt/backlog-backup/releases).

#### Usage

On Windows:
```
backlog-backup-win.exe --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all
```

On macOS/Linux:
```
chmod +x backlog-backup-macos  # Make executable (first time only)
./backlog-backup-macos --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all
```

### Build your own executable

To build a standalone executable:

```bash
# Clone the repository
git clone https://github.com/tmyymmt/backlog-backup.git
cd backlog-backup

# Install required dependencies
pip install -e ".[build]"

# Build the executable
python build_executable.py

# For a single-file executable
python build_executable.py --one-file

# For a Windows executable with no console window
python build_executable.py --no-console

# Customize the output name and location
python build_executable.py --name custom-name --output-dir ./my-builds
```

The executable will be created in the `dist` directory by default.

#### Advanced customization

For advanced customization of the build process, you can modify the included `backlog-backup.spec` file and use PyInstaller directly:

```bash
# Install PyInstaller
pip install pyinstaller>=5.8.0

# Edit backlog-backup.spec file to customize the build
# Then build using the spec file
pyinstaller backlog-backup.spec
```

### Using Docker

```bash
# Clone the repository
git clone https://github.com/tmyymmt/backlog-backup.git
cd backlog-backup

# Build the Docker image
docker build -t backlog-backup .

# Run the container
docker run -v $(pwd)/backup:/app/backup backlog-backup --help

# Run with environment variable for API key
docker run -v $(pwd)/backup:/app/backup -e BACKLOG_API_KEY=YOUR_API_KEY backlog-backup --domain example.backlog.com --project PROJECT_KEY --all
```

## Usage

### Authentication

The tool requires a Backlog API key for accessing project data. Additionally, for backing up Git and Subversion repositories, separate authentication credentials may be required.

#### API Key
- Set via `--api-key` parameter or `BACKLOG_API_KEY` environment variable
- Required for all operations

#### Git/SVN Repository Authentication
- Set via `--git-username`/`--git-password` parameters or `BACKLOG_GIT_USERNAME`/`BACKLOG_GIT_PASSWORD` environment variables for Git
- Set via `--svn-username`/`--svn-password` parameters or `BACKLOG_SVN_USERNAME`/`BACKLOG_SVN_PASSWORD` environment variables for SVN
- Required only when backing up repositories that require authentication

**Security Note**: For security reasons, it's recommended to use environment variables instead of command-line parameters for passwords and API keys, as command-line arguments may be visible in process lists.

### Basic Usage

```bash
# List all accessible projects
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --list-projects

# List all non-archived projects in the space (requires admin privileges)
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --list-projects --include-all-space-projects --archived-projects non-archived-only

# Backup issues for a project
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --issues --output ./backup

# Backup everything for a project
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --output ./backup

# Use API key from environment variable
export BACKLOG_API_KEY=YOUR_API_KEY
backlog-backup --domain example.backlog.com --project PROJECT_KEY --all --output ./backup

# Use Git/SVN authentication for repository backup
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --git --svn --git-username YOUR_GIT_USERNAME --git-password YOUR_GIT_PASSWORD --svn-username YOUR_SVN_USERNAME --svn-password YOUR_SVN_PASSWORD --output ./backup

# Use environment variables for all authentication
export BACKLOG_API_KEY=YOUR_API_KEY
export BACKLOG_GIT_USERNAME=YOUR_GIT_USERNAME
export BACKLOG_GIT_PASSWORD=YOUR_GIT_PASSWORD
export BACKLOG_SVN_USERNAME=YOUR_SVN_USERNAME
export BACKLOG_SVN_PASSWORD=YOUR_SVN_PASSWORD
backlog-backup --domain example.backlog.com --project PROJECT_KEY --all --output ./backup

# Backup all accessible projects
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --all-projects --all --output ./backup

# Backup only non-archived projects
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --all-projects --archived-projects non-archived-only --all --output ./backup
```

### Advanced Usage Examples

```bash
# Backup only issues and wiki (exclude files and repositories)
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --issues --wiki --output ./backup

# Backup all data including repositories with authentication
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --git-username user@example.com --git-password yourpassword --svn-username user@example.com --svn-password yourpassword --output ./backup

# List only archived projects (requires admin privileges)
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --list-projects --include-all-space-projects --archived-projects archived-only

# Backup to a custom directory with verbose output
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --output /path/to/backup --verbose
```

### Command Line Options

```
--version             Show version information
-v, --verbose         Enable verbose output
--domain DOMAIN       Backlog domain (e.g., 'example.backlog.com')
--api-key API_KEY     Backlog API key (can also be set via BACKLOG_API_KEY environment variable)
--git-username        Username for Git repository authentication (can also be set via BACKLOG_GIT_USERNAME environment variable)
--git-password        Password for Git repository authentication (can also be set via BACKLOG_GIT_PASSWORD environment variable)
--svn-username        Username for SVN repository authentication (can also be set via BACKLOG_SVN_USERNAME environment variable)
--svn-password        Password for SVN repository authentication (can also be set via BACKLOG_SVN_PASSWORD environment variable)
--project PROJECT     Backlog project key to backup
--all-projects        Backup all accessible projects
--list-projects       List all accessible projects
--include-all-space-projects
                      Include all projects in the space, not just those the user has access to (requires admin privileges)
--archived-projects {all,archived-only,non-archived-only}
                      Filter projects by archive status (default: 'all')
--output OUTPUT, -o OUTPUT
                      Output directory for backup (default: './backup')
--issues              Backup project issues
--wiki                Backup project wiki
--files               Backup project files
--git                 Backup Git repositories
--svn                 Backup Subversion repositories
--all                 Backup everything
```

### Using Docker Compose

1. Edit the `docker-compose.yml` file to include your parameters
2. Run the backup:

```bash
docker-compose up
```

## Troubleshooting

### Common Issues

#### Authentication Errors
- **API Key Issues**: Ensure your API key is valid and has the necessary permissions for the projects you're trying to access.
- **Repository Authentication**: Git/SVN repositories may require separate authentication credentials from your API key.

#### Permission Errors
- **Admin Privileges Required**: Some operations like `--include-all-space-projects` require administrator privileges in your Backlog space.
- **Project Access**: Ensure you have access to the projects you're trying to backup.

#### Network and Rate Limiting
- **API Rate Limits**: The tool automatically handles Backlog API rate limits, but very large projects may take significant time to backup.
- **Web Scraping Fallback**: When API access is limited, the tool falls back to web scraping with appropriate rate limiting (1 request per second).

#### File and Directory Issues
- **Output Directory**: Ensure the output directory is writable and has sufficient disk space.
- **Large Files**: Very large file attachments may take considerable time to download.

### Debug Mode

For detailed troubleshooting information, use the verbose flag:

```bash
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --verbose
```

## Directory Structure

The backup tool creates the following directory structure:

```
output_directory/
└── project_key/
    ├── issues/
    │   ├── issue_list.csv          # Summary of all issues in CSV format
    │   ├── ISSUE-1.json           # Detailed issue data in JSON format
    │   ├── ISSUE-2.json
    │   └── attachments/
    │       └── ISSUE-1/
    │           └── attachment1.png # Issue attachments
    ├── wiki/
    │   ├── wiki_index.json        # Wiki pages index
    │   ├── Page1.json             # Wiki page data in JSON format
    │   ├── Page1.md              # Wiki page content in Markdown format
    │   └── attachments/
    │       └── Page1/
    │           └── attachment1.png # Wiki page attachments
    ├── files/
    │   └── directory_structure_mirroring_backlog  # Project files maintaining original directory structure
    ├── git/
    │   └── repository1/           # Git repository clone
    └── svn/
        └── repository1/           # SVN repository checkout
```

### File Format Details

- **Issues**: 
  - `issue_list.csv`: Contains summary information of all issues (ID, title, status, assignee, etc.)
  - `ISSUE-{number}.json`: Complete issue data including comments, attachments, and change history
  - Attachments are downloaded and organized by issue

- **Wiki**: 
  - `wiki_index.json`: Index of all wiki pages with metadata
  - `{page_name}.json`: Complete page data including content and metadata
  - `{page_name}.md`: Page content extracted as Markdown for easy reading
  - Attachments are downloaded and organized by page

- **Files**: Original Backlog file structure is preserved
- **Repositories**: Full repository clones/checkouts for offline access

## License

MIT-0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -e ".[scraping,build]"`
3. Run tests: `python -m pytest tests/`

## References

- [Backlog](https://backlog.com/)
- [Backlog API](https://developer.nulab.com/docs/backlog/)