#!/usr/bin/env bash
mkdir -p data

echo "Downloading recent files from S3..."
recent_files=`aws s3 ls ${AWS_S3_BUCKET}/news/ | awk '{print $4}' | sort | tail -n 180`
while IFS= read -r line; do
  if [ ! -f data/${line} ]; then
    aws s3 cp --no-progress s3://${AWS_S3_BUCKET}/news/${line} data/ &
    sleep 0.5
  fi
done <<< "${recent_files}"
wait

echo "Unzipping files..."
gunzip -kf data/*.csv.gz

echo "Analyzing..."
python cli.py tag_and_stats
