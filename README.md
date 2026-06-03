# Netflix Continue Watching Scraper

A Python automation tool that extracts data from the Netflix "Continue Watching" section, generates an Excel report, and emails the report automatically.

## Features

- Uses stored Netflix cookies for authentication
- Automatic login session reuse
- Detects expired cookies
- Redirects user for manual login when required
- Saves fresh cookies automatically
- Extracts Continue Watching information
- Generates Excel reports
- Sends reports via email

## Information Collected

For Movies:
- Movie title
- Remaining watch time

For Series:
- Series title
- Current season
- Remaining episodes in each season

## How It Works

1. The program loads previously saved Netflix cookies.
2. If cookies are valid:
   - User is logged in automatically.
3. If cookies are expired:
   - User logs in manually.
   - New cookies are stored.
4. Continue Watching data is scraped.
5. An Excel report is generated.
6. The report is emailed to the specified email address.

## Technologies Used

- Python
- Selenium
- OpenPyXL
- SMTP
- Cookies-based Authentication

## Installation

```bash
git clone <repository-url>
cd netflix-scraper
pip install -r requirements.txt
