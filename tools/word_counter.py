#!/usr/bin/env python3
"""字数统计工具 - Word Count Tool"""
import re, json, sys
from pathlib import Path

def count_file(filepath):
    content = Path(filepath).read_text(encoding='utf-8')
    chars = len(content)
    words = len(re.findall(r'\S+', content))
    paragraphs = len([p for p in content.split('\n\n') if p.strip()])
    sentences = len(re.split(r'[。！？.!?]', content)) - 1
    return {
        'file': filepath,
        'chars': chars,
        'words': words,
        'paragraphs': paragraphs,
        'sentences': sentences,
    }

if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(json.dumps(count_file(f), ensure_ascii=False, indent=2))
