#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <input_folder>"
    exit 1
fi

input_dir="$1"

for file in "$input_dir"/*.mp4; do
    tmp_file="${file}.tmp.mp4"  # 임시 파일
    echo "Processing $file -> $tmp_file"

    ffmpeg -i "$file" -c:v libx264 -pix_fmt yuv420p -movflags faststart -y "$tmp_file"

    # 변환 완료 후 원본 덮어쓰기
    mv -f "$tmp_file" "$file"
done