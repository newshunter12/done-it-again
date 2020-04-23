#!/usr/bin/env bash
mkdir -p docs/_data/

echo "Downloading files from S3..."
aws s3 sync --quiet s3://${AWS_S3_BUCKET}/done-it-again-analysis/ docs/_data/
