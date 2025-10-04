#!/usr/bin/env python3
"""
scripts/update_helm.py

Atualiza apenas:
 - k8s/values.yaml -> image.repository e image.tag (preservando o restante)
 - k8s/Chart.yaml  -> appVersion

Uso:
  python scripts/update_helm.py --values k8s/values.yaml --chart k8s/Chart.yaml \
    --image-full ghcr.io/org/repo:1.2.3 --image-tag 1.2.3
"""
from pathlib import Path
import argparse
import yaml
import shutil
import sys

def load_yaml(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def dump_yaml(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data or {}, f, sort_keys=False, allow_unicode=True)

def backup(path: Path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, bak)
        print(f"Backup created: {bak}")

def update_values(values_path: Path, image_full: str, image_tag: str):
    # load existing values (if any)
    vals = load_yaml(values_path)
    if vals is None:
        vals = {}
        print(f"Warning: {values_path} did not exist or was empty. Creating new file.")

    # ensure 'image' key exists as dict if possible
    img = vals.get("image")
    if img is None:
        # create image mapping with sensible defaults
        img = {}
    if isinstance(img, dict):
        # set repository and tag while leaving other subkeys (pullPolicy etc) intact
        repo = image_full.rsplit(":", 1)[0]
        img["repository"] = repo
        img["tag"] = image_tag
        vals["image"] = img
    else:
        # if image is a non-dict (string), set to full image string
        vals["image"] = image_full

    dump_yaml(values_path, vals)
    print(f"Updated {values_path}: image.repository={repo if isinstance(img, dict) else image_full}, image.tag={image_tag}")

def update_chart(chart_path: Path, image_tag: str):
    chart = load_yaml(chart_path)
    if chart is None:
        chart = {}
        print(f"Warning: {chart_path} did not exist or was empty. Creating new Chart.yaml.")

    chart["appVersion"] = image_tag
    dump_yaml(chart_path, chart)
    print(f"Updated {chart_path}: appVersion={image_tag}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--values", required=True, help="Path to values.yaml")
    parser.add_argument("--chart", required=True, help="Path to Chart.yaml")
    parser.add_argument("--image-full", required=True, help="Full image name (repo:tag)")
    parser.add_argument("--image-tag", required=True, help="Image tag (semver)")
    args = parser.parse_args()

    values_path = Path(args.values)
    chart_path = Path(args.chart)

    # backups
    backup(values_path)
    backup(chart_path)

    update_values(values_path, args.image_full, args.image_tag)
    update_chart(chart_path, args.image_tag)

if __name__ == "__main__":
    main()
