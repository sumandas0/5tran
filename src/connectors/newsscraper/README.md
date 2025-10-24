# newsscraper Connector

This Fivetran connector extracts data from: https://news.google.com

## Files

- `connector.py`: The main connector implementation
- `configuration.json`: Configuration with API keys and URL
- `requirements.txt`: Python dependencies

## Setup

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Testing Locally

```bash
python connector.py
```

## Deploying to Fivetran

```bash
fivetran deploy src/connectors/newsscraper
```

Make sure you have the Fivetran CLI installed and configured.
