#!/usr/bin/env python3
"""
scripts/update_helm.py

Uso:
  python scripts/update_helm.py --values k8s/values.yaml --chart k8s/Chart.yaml --image-full ghcr.io/org/repo:1.2.3 --image-tag 1.2.3

Este script atualiza:
 - values.yaml: coloca a imagem (como bloco image.repository/tag ou string full) 
 - Chart.yaml: atualiza appVersion para a tag fornecida
"""
import argparse
import yaml
from pathlib import Path
import sys

def load_yaml(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def dump_yaml(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data or {}, f, sort_keys=False, allow_unicode=True)

def update_values(values_path: Path, image_full: str, image_tag: str):
    vals = load_yaml(values_path) or {}
    img = vals.get("image")
    if isinstance(img, dict):
        repo = image_full.rsplit(":", 1)[0]
        img["repository"] = repo
        img["tag"] = image_tag
        vals["image"] = img
    else:
        # se era string ou inexistente, gravamos a string completa
        vals["image"] = image_full
    dump_yaml(values_path, vals)
    print(f"Updated {values_path} -> image: {image_full}")

def update_chart(chart_path: Path, image_tag: str):
    chart = load_yaml(chart_path) or {}
    chart["appVersion"] = image_tag
    dump_yaml(chart_path, chart)
    print(f"Updated {chart_path} -> appVersion: {image_tag}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--values", required=True, help="Caminho para k8s/values.yaml")
    p.add_argument("--chart", required=True, help="Caminho para k8s/Chart.yaml")
    p.add_argument("--image-full", required=True, help="Imagem completa (repo:tag)")
    p.add_argument("--image-tag", required=True, help="Tag semver (ex: 1.2.3)")
    args = p.parse_args()

    values_path = Path(args.values)
    chart_path = Path(args.chart)

    if not values_path.exists():
        print(f"Warning: values file {values_path} does not exist. Will create it.", file=sys.stderr)
    if not chart_path.exists():
        print(f"Warning: chart file {chart_path} does not exist. Will create it.", file=sys.stderr)

    update_values(values_path, args.image_full, args.image_tag)
    update_chart(chart_path, args.image_tag)

if __name__ == "__main__":
    main()
