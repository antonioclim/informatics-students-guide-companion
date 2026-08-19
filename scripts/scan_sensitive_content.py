#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, io, re, sys, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '__pycache__', '_qa', '_build'}
TEXT_SUFFIXES = {'.md', '.txt', '.csv', '.json', '.yml', '.yaml', '.xml', '.svg', '.cff', '.py', '.sh', '.gitignore', '.gitattributes'}
ARCHIVE_TEXT_SUFFIXES = {'.xml', '.rels', '.txt', '.csv', '.json', '.md', '.yml', '.yaml'}
PATTERNS = [
    ('private_key', 'high', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
    ('github_token', 'high', re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b')),
    ('generic_secret_assignment', 'high', re.compile(r'(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*["\']?[A-Za-z0-9_\-./+=]{16,}')),
    ('email', 'medium', re.compile(r'(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])', re.I)),
    ('romanian_phone', 'medium', re.compile(r'(?<!\d)(?:\+40|0040|0)7\d{8}(?!\d)')),
    ('windows_user_path', 'medium', re.compile(r'(?i)\b[A-Z]:\\Users\\[^\\\s]+')),
    ('unix_private_path', 'medium', re.compile(r'/(?:home|Users|mnt/data)/[^\s"\']+')),
]
ALLOWED_EMAILS = set()


def scan_text(name: str, text: str, hits: list[dict]) -> None:
    for lineno, line in enumerate(text.splitlines(), 1):
        for label, severity, rx in PATTERNS:
            for m in rx.finditer(line):
                value = m.group(0)
                if label == 'email' and value.lower() in ALLOWED_EMAILS:
                    continue
                hits.append({'file': name, 'line': lineno, 'pattern': label, 'severity': severity, 'value': value, 'context': line[:500]})


def read_candidate(path: Path):
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES or path.name in {'.gitignore', '.gitattributes'}:
        yield path.relative_to(ROOT).as_posix(), path.read_text(encoding='utf-8', errors='replace')
    elif suffix in {'.docx', '.xlsx', '.odg', '.pptx'}:
        try:
            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    if Path(name).suffix.lower() in ARCHIVE_TEXT_SUFFIXES:
                        yield f'{path.relative_to(ROOT).as_posix()}::{name}', zf.read(name).decode('utf-8', errors='replace')
        except zipfile.BadZipFile:
            yield path.relative_to(ROOT).as_posix(), ''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--fail-on', choices=['high', 'medium', 'none'], default='medium')
    ap.add_argument('--csv', default='')
    args = ap.parse_args()
    hits=[]
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        for name, text in read_candidate(path):
            scan_text(name, text, hits)
    if args.csv:
        out = Path(args.csv)
        with out.open('w', encoding='utf-8-sig', newline='') as f:
            w=csv.DictWriter(f, fieldnames=['file','line','pattern','severity','value','context'])
            w.writeheader(); w.writerows(hits)
    for hit in hits:
        print(f"{hit['severity'].upper()}: {hit['file']}:{hit['line']} {hit['pattern']} {hit['value']}")
    levels={'high':2,'medium':1,'none':0}
    threshold=levels[args.fail_on]
    fail=any(levels.get(h['severity'],0)>=threshold for h in hits) if threshold else False
    print(f'SCAN: {len(hits)} finding(s); fail-on={args.fail_on}; status={"FAIL" if fail else "PASS"}')
    return 1 if fail else 0

if __name__ == '__main__':
    raise SystemExit(main())
