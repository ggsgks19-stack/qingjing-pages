# -*- coding: utf-8 -*-
"""合并 GKD 订阅：雾栈定制 + AIsouler + 甘霖 -> dist/wuzhan_gkd.json5
用法: python merge.py  （在仓库根目录运行）
以后社区库有更新: 重新下载 sources/ 下两个文件，重跑本脚本即可。
"""
import json, json5, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(p):
    return json5.loads(io.open(os.path.join(ROOT, p), encoding='utf-8').read())

mine = load('sources/wuzhan_gkd.json5')
aisouler = load('sources/AIsouler_gkd.json5')
ganlin = load('sources/ganlin_gkd.json5')

SOURCES = [mine, aisouler, ganlin]

# ---- categories：按源偏移 key，避免冲突（每源预留 100）----
categories = []
for si, sub in enumerate(SOURCES):
    off = si * 100
    for c in sub.get('categories', []):
        c = dict(c)
        c['key'] = c['key'] + off
        categories.append(c)
CAT_OFF = {si: si * 100 for si in range(len(SOURCES))}

# ---- globalGroups：key 每源偏移 1000 ----
globalGroups = []
for si, sub in enumerate(SOURCES):
    off = si * 1000
    for g in sub.get('globalGroups', []):
        g = dict(g)
        g['key'] = g['key'] + off
        globalGroups.append(g)

# ---- apps：按包名合并，组 key 重新顺序编号，category 引用重映射 ----
apps = {}
order = []
for si, sub in enumerate(SOURCES):
    off = CAT_OFF[si]
    for a in sub.get('apps', []):
        aid = a['id']
        if aid not in apps:
            apps[aid] = {'id': aid, 'name': a.get('name', aid), 'groups': []}
            order.append(aid)
        dst = apps[aid]
        seen = set(g.get('key') for g in dst['groups'])
        for g in a.get('groups', []):
            g = dict(g)
            if 'category' in g:
                g['category'] = g['category'] + off
            # 组 key 唯一化：冲突就往后排
            k = g.get('key')
            if k is None or k in seen:
                k = (max(seen) + 1) if seen else 0
            seen.add(k)
            g['key'] = k
            dst['groups'].append(g)

merged = {
    'id': 20261009,
    'name': '雾栈清净规则',
    'version': 2026100902,
    'author': '雾栈',
    'checkUpdateUrl': 'https://cdn.jsdelivr.net/gh/ggsgks19-stack/qingjing-pages@main/wuzhan_gkd.json5',
    'supportUri': 'https://github.com/ggsgks19-stack/qingjing-pages',
    'categories': categories,
    'globalGroups': globalGroups,
    'apps': [apps[i] for i in order],
}

out = os.path.join(ROOT, 'wuzhan_gkd.json5')
io.open(out, 'w', encoding='utf-8').write(json.dumps(merged, ensure_ascii=False, indent=1))

n_groups = sum(len(apps[i]['groups']) for i in order)
print('merged OK: apps=%d groups=%d globalGroups=%d size=%.1fMB' % (
    len(order), n_groups, len(globalGroups), os.path.getsize(out) / 1048576))
