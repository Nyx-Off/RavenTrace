<div align="center">

# RavenTrace

![Logo](https://github.com/Nyx-Off/RavenTrace/blob/main/logo.png)

![RAVEN TRACE LOGO](https://img.shields.io/badge/Raven%20Trace-v2.0.1-a800c6?style=for-the-badge)

**Advanced OSINT Intelligence Tool**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)]()
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-green?style=flat-square)]()

*Powerful OSINT reconnaissance tool for Email, Phone, and Username investigations*

[Features](#-features) • [Installation](https://github.com/Nyx-Off/RavenTrace/blob/main/README_INSTALLATION.md) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

**RavenTrace** is a comprehensive Open Source Intelligence (OSINT) gathering tool designed for cybersecurity professionals, researchers, and investigators. It provides deep reconnaissance capabilities across multiple data sources to gather intelligence on email addresses, phone numbers, and usernames.

### 🌟 Key Highlights

- **🔍 Multi-Vector Search**: Simultaneous investigation across emails, phones, and usernames
- **⚡ Real-Time Data**: Live queries to 20+ platforms and APIs
- **🛡️ Privacy-Focused**: Responsible data gathering with rate limiting
- **📊 Smart Caching**: SQLite-based intelligent caching system
- **🎨 Beautiful CLI**: Rich terminal interface with interactive mode
- **📈 Confidence Scoring**: AI-powered result reliability assessment

## ✨ Features

### 📧 Email Intelligence
- ✅ **Reputation Analysis** (EmailRep.io integration)
- ✅ **DNS Records Investigation** (MX, SPF, DMARC verification)
- ✅ **Data Breach Detection** (Have I Been Pwned API)
- ✅ **Social Media Discovery** (LinkedIn, GitHub, Twitter)
- ✅ **Domain WHOIS Lookup**
- ✅ **Email Pattern Analysis**

### 📱 Phone Intelligence
- ✅ **Carrier Identification** (Global carrier detection)
- ✅ **Geographic Location** (Country, region, timezone)
- ✅ **Reputation Checking** (TrueCaller, NumVerify)
- ✅ **VoIP Detection** (Identify virtual numbers)
- ✅ **Data Broker Search** (WhitePages, Spokeo)
- ✅ **Spam Report Analysis**

### 👤 Username Intelligence
- ✅ **20+ Platform Search** (Social media presence)
- ✅ **GitHub Deep Dive** (Repos, followers, activity)
- ✅ **Reddit Analysis** (Karma, posts, communities)
- ✅ **Developer Platforms** (StackOverflow, Dev.to, Medium)
- ✅ **Gaming Platforms** (Steam, Discord, Twitch)
- ✅ **Professional Networks** (LinkedIn, GitLab)

### 🔧 Advanced Features
- 🚀 **Parallel Processing** (ThreadPoolExecutor optimization)
- 💾 **Smart Cache System** (24-hour TTL, SQLite backend)
- 📊 **Multiple Export Formats** (JSON, CSV, HTML reports)
- 🎯 **Confidence Scoring** (Result reliability metrics)
- 📝 **Detailed Reporting** (Professional HTML reports)
- 🔄 **Rate Limit Protection** (Respectful API usage)
- 🎭 **User-Agent Rotation** (Anti-detection measures)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Quick Install

[Installation](https://github.com/Nyx-Off/RavenTrace/blob/main/README_INSTALLATION.md)

### Dependencies

Core dependencies include:
- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing
- `phonenumbers` - Phone number validation
- `email-validator` - Email validation
- `rich` - Terminal formatting
- `click` - CLI framework
- `dnspython` - DNS lookups

## 📖 Usage

### Command Line Interface

#### Basic Commands

```bash
# Email search
raven-trace email user@example.com

# Phone search
raven-trace phone +33612345678 --country FR

# Username search
raven-trace username john_doe

# Batch search
raven-trace batch user@example.com john_doe +33612345678
```

#### Advanced Options

```bash
# Deep scan with all sources
raven-trace email user@example.com --deep

# Export results
raven-trace username john_doe --export json
raven-trace email user@example.com --export html

# Interactive mode
raven-trace interactive
```

### Interactive Mode

Launch the interactive terminal UI:

```bash
raven-trace interactive
```

Features:
- 🎨 Beautiful menu interface
- 🔍 Guided search workflows
- 📊 Real-time results display
- 💾 Automatic result saving
- ⚙️ Configuration management

### Python API

```python
from core.engine import SearchEngine

# Initialize engine
engine = SearchEngine()

# Email search
email_results = engine.search_email("target@example.com", deep_scan=True)
print(f"Confidence: {email_results['confidence']}%")
print(f"Breaches found: {len(email_results['breaches'])}")

# Username search
username_results = engine.search_username("john_doe")
print(f"Profiles found: {username_results['profiles_found']}")

# Phone search
phone_results = engine.search_phone("+33612345678", country="FR")
print(f"Carrier: {phone_results['carrier_info']['carrier']}")

# Export results
engine.export_results(email_results, format_type='html', filepath='report.html')
```

## 📁 Project Structure

```
.
├── cli
│   ├── __init__.py
│   └── interface.py
├── config.py
├── config.yaml
├── core
│   ├── engine.py
│   ├── __init__.py
│   ├── scrapers.py
│   └── validators.py
├── __init__.py
├── install_kali_tools.sh
├── LICENSE
├── main.py
├── modules
│   ├── advanced_osint.py
│   ├── breaches.py
│   ├── email_lookup.py
│   ├── __init__.py
│   ├── kali_tools.py
│   ├── phone_lookup.py
│   ├── reporting.py
│   └── username_lookup.py
├── README_INSTALLATION.md
├── README.md
├── requirements.txt
├── setup.py
├── setup_venv.sh
├── sources
│   ├── data_aggregators.py
│   ├── __init__.py
│   ├── public_apis.py
│   └── social_media.py
├── storage
│   ├── database.py
│   └── __init__.py
├── tests
│   └── test_core.py
├── utils
│   ├── formatter.py
│   ├── helpers.py
│   ├── __init__.py
│   └── logger.py
└── venv
    ├── bin
    │   ├── python -> python3
    │   ├── python3 -> /usr/bin/python3
    │   └── python3.13 -> python3
    └── lib64 -> lib

```

## 🔍 Data Sources

### Integrated APIs & Platforms

| Category | Sources |
|----------|---------|
| **Email** | EmailRep.io, Have I Been Pwned, DNS Records, WHOIS |
| **Phone** | TrueCaller, NumVerify, WhitePages, Spokeo |
| **Social** | GitHub, LinkedIn, Twitter, Instagram, Facebook |
| **Forums** | Reddit, StackOverflow, Medium, Dev.to |
| **Gaming** | Steam, Discord, Twitch |
| **Professional** | GitLab, Patreon, Behance |

## 🛠️ Configuration

### Environment Variables

```bash
# Optional API keys for enhanced results
export SHODAN_API_KEY="your_key"
export HUNTER_API_KEY="your_key"
export CLEARBIT_API_KEY="your_key"
```

### Configuration File

Create `config.yaml`:

```yaml
search:
  timeout: 10
  workers: 5
  rotate_user_agent: true
  rate_limit: 30

cache:
  ttl_hours: 24
  auto_cleanup: true

output:
  default_format: table
  show_confidence: true
```

## 📊 Output Examples

### Email Search Result
```json
{
  "email": "user@example.com",
  "confidence": 85.5,
  "reputation": {
    "score": "high",
    "suspicious": false
  },
  "breaches": [
    {
      "name": "Example Breach",
      "date": "2023-01-01",
      "severity": "HIGH"
    }
  ],
  "social_profiles": ["github", "linkedin"],
  "dns": {
    "mx_records": 3,
    "spf_configured": true,
    "dmarc_configured": false
  }
}
```

## 🔒 Security & Privacy

### Ethical Guidelines

- ✅ **Legal Use Only** - Comply with local laws and regulations
- ✅ **Respect Privacy** - Only investigate with proper authorization
- ✅ **Rate Limiting** - Respectful API usage to prevent server overload
- ✅ **No Illegal Access** - No hacking or unauthorized access attempts
- ✅ **GDPR Compliant** - Respect data protection regulations

### Best Practices

1. Always obtain permission before investigating individuals
2. Use for legitimate security research only
3. Respect platform Terms of Service
4. Implement proper data handling procedures
5. Maintain audit logs of searches

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/yourusername/raven-trace.git
cd raven-trace
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest tests/

# Code formatting
black .
flake8 .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Have I Been Pwned](https://haveibeenpwned.com/) - Data breach information
- [EmailRep.io](https://emailrep.io/) - Email reputation data
- [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) - Phone number parsing
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting

## ⚠️ Disclaimer

**RavenTrace is designed for educational and legitimate security research purposes only.**

The developers assume no liability and are not responsible for any misuse or damage caused by this tool. Users are solely responsible for complying with all applicable laws and regulations in their jurisdiction.

This tool should only be used:
- With explicit permission from the target
- For legitimate security assessments
- In compliance with all applicable laws
- Following ethical guidelines

## 📞 Contact

**Author**: Samy - Nyx  
**Email**: Samy.bensalem@etik.com  
**Project Link**: [https://github.com/yourusername/raven-trace](https://github.com/yourusername/raven-trace)

---

<div align="center">

**RavenTrace** - *Intelligence at Your Fingertips* 🐦

Made with ❤️ by ME

</div>






