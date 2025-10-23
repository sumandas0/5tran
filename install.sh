#!/bin/bash
# Quick install script for 5tran

echo "Installing 5tran CLI..."

# Install dependencies
uv sync

echo "✓ 5tran installed!"
echo ""
echo "Usage:"
echo "  5tran generate pipeline 'description' --spec openapi.yaml"
echo "  5tran deploy pipeline --config .5tran.yml"
echo "  5tran status check"
echo ""
echo "Set credentials:"
echo "  export FIVETRAN_API_KEY='your_key'"
echo "  export FIVETRAN_API_SECRET='your_secret'"

