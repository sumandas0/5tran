# asianews01 Connector

This Fivetran connector extracts data from: https://www.bbc.com/news/world/asia

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
fivetran deploy src/connectors/asianews01
```

Make sure you have the Fivetran CLI installed and configured.
