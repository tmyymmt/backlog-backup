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

### Basic Usage

```bash
# List all accessible projects
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --list-projects

# Backup issues for a project
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --issues --output ./backup

# Backup everything for a project
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --project PROJECT_KEY --all --output ./backup

# Use API key from environment variable
export BACKLOG_API_KEY=YOUR_API_KEY
backlog-backup --domain example.backlog.com --project PROJECT_KEY --all --output ./backup

# Backup all accessible projects
backlog-backup --domain example.backlog.com --api-key YOUR_API_KEY --all-projects --all --output ./backup
```

### Command Line Options

```
--version             Show version information
-v, --verbose         Enable verbose output
--domain DOMAIN       Backlog domain (e.g., 'example.backlog.com')
--api-key API_KEY     Backlog API key (can also be set via BACKLOG_API_KEY environment variable)
--project PROJECT     Backlog project key to backup
--all-projects        Backup all accessible projects
--list-projects       List all accessible projects
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

## Directory Structure

The backup tool creates the following directory structure:

```
output_directory/
└── project_key/
    ├── issues/
    │   ├── issue_list.csv
    │   ├── ISSUE-1.json
    │   ├── ISSUE-2.json
    │   └── attachments/
    │       └── ISSUE-1/
    │           └── attachment1.png
    ├── wiki/
    │   ├── wiki_index.json
    │   ├── Page1.json
    │   ├── Page1.md
    │   └── attachments/
    │       └── Page1/
    │           └── attachment1.png
    ├── files/
    │   └── directory_structure_mirroring_backlog
    ├── git/
    │   └── repository1/
    └── svn/
        └── repository1/
```

## License

MIT-0

## References

- [Backlog](https://backlog.com/)
- [Backlog API](https://developer.nulab.com/docs/backlog/)