#!/usr/bin/env python3
"""AI味检测工具 - AI Smell Detector"""
import re, json, sys
from pathlib import Path

AI_KEYWORDS = {
    '总体': 0, '首先': 0, '其次': 0, '最后': 0, '总的来说': 0,
    '值得注意的是': 0, '不可否认': 0, '从这个角度': 0,
    '确实': 0, '当然': 0, '毫无疑问': 0,
    '拥有': 0, '展现': 0, '凸显': 0, '诠释': 0, '彰显': 0,
    '标志着': 0, '意味着': 0, '那么': 0, '然后': 0, '于是': 0,
    '此外': 0, '然而': 0, '在这一刻': 0, '此时此刻': 0,
    '仿佛': 0, '似乎': 0, '好像': 0, '犹如': 0, '如同': 0,
    '缓缓': 0, '轻轻': 0, '微微': 0, '渐渐': 0, '默默': 0,
    '感受到': 0, '意识到': 0, '感觉到': 0, '体会到': 0, '注意到': 0,
}

def detect(filepath):
    content = Path(filepath).read_text(encoding='utf-8')
    words = len(re.findall(r'\S+', content))
    hits = []
    total_hits = 0
    
    for kw in AI_KEYWORDS:
        count = len(re.findall(kw, content))
        if count > 0:
            hits.append({'keyword': kw, 'count': count})
            total_hits += count
    
    density = round(total_hits / words * 1000, 2) if words > 0 else 0
    grade = '优秀' if density < 3 else '良好' if density < 6 else '及格' if density < 12 else '需要改进'
    
    return {
        'file': filepath,
        'total_words': words,
        'ai_hits': total_hits,
        'density_per_1000': density,
        'grade': grade,
        'top_issues': sorted(hits, key=lambda x: -x['count'])[:5],
    }

if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(json.dumps(detect(f), ensure_ascii=False, indent=2))
