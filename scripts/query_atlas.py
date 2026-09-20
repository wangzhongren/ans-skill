#!/usr/bin/env python3
"""Query a current local atlas as bounded JSON; edges are file references, not runtime traces."""
import argparse
from collections import deque
import json
from pathlib import Path
import sys

import sync_atlas as sync


def validate(data):
    if not isinstance(data, dict) or data.get('schemaVersion') != 1:
        raise ValueError('Expected atlas schemaVersion 1')
    if not isinstance(data.get('files'), list) or not isinstance(data.get('edges'), list):
        raise ValueError('files and edges must be arrays')
    nodes = {}
    for node in data['files']:
        if not isinstance(node, dict) or not sync.safe_path(node.get('id')) or node.get('path') != node['id'] or node['id'] in nodes:
            raise ValueError('Invalid or duplicate file ID')
        nodes[node['id']] = node
    for edge in data['edges']:
        if not isinstance(edge, dict) or edge.get('source') not in nodes or edge.get('target') not in nodes:
            raise ValueError('Invalid edge endpoint')
        if type(edge.get('line')) is not int or edge['line'] < 1 or not isinstance(edge.get('kind'), str) or not isinstance(edge.get('evidence'), str):
            raise ValueError('Edge requires positive line, kind, and evidence')
    return nodes


def freshness(data, root, source_root=None):
    current = sync.scan(root.resolve(), source_root)
    sync.review(current, data)
    keys = ['sourceFingerprint', 'sourceBaseUri', 'sourceRoots', 'files', 'edges', 'unresolved', 'dynamic', 'external', 'parseErrors', 'coverage', 'cycles', 'annotations', 'aiRelations', 'reviewWarnings']
    changed = [k for k in keys if data.get(k) != current.get(k)]
    if data.get('scannerHash') != sync.digest(Path(sync.__file__).read_bytes()):
        changed.append('scannerHash')
    return changed


def query(data, file=None, direction='dependencies', impact=False, start=None, target=None, max_depth=20, limit=100, max_nodes=10000):
    nodes = validate(data)
    origin = start if start is not None else file
    for name in [origin, target]:
        if name is not None and name not in nodes:
            raise ValueError('File not found in scoped inventory: ' + name)
    outgoing = {n: [] for n in nodes}
    incoming = {n: [] for n in nodes}
    for e in data['edges']:
        outgoing[e['source']].append(e)
        incoming[e['target']].append(e)
    for graph in [outgoing, incoming]:
        for edges in graph.values():
            edges.sort(key=lambda e: (e['source'], e['target'], e['line'], e['kind']))
    result = {'query': 'path' if start is not None else 'impact' if impact else direction,
              'origin': origin, 'target': target, 'truncated': False, 'bounds': {'maxDepth': max_depth, 'limit': limit, 'maxNodes': max_nodes}}
    involved = {origin}
    if start is None and not impact:
        edges = (incoming if direction == 'callers' else outgoing)[origin]
        result['edges'] = edges[:limit]
        result['totalEdges'] = len(edges)
        result['truncated'] = len(edges) > limit
        involved.update(e['source'] for e in result['edges'])
        involved.update(e['target'] for e in result['edges'])
    else:
        reverse = impact
        graph = incoming if reverse else outgoing
        depth = {origin: 0}
        parent = {}
        queue = deque([origin])
        reasons = set()
        while queue:
            current = queue.popleft()
            if not impact and current == target:
                break
            for e in graph[current]:
                neighbor = e['source'] if reverse else e['target']
                if neighbor in depth:
                    continue
                if depth[current] >= max_depth:
                    reasons.add('maxDepth')
                    continue
                if len(depth) >= max_nodes:
                    reasons.add('maxNodes')
                    continue
                depth[neighbor] = depth[current] + 1
                parent[neighbor] = (current, e)
                queue.append(neighbor)
        if impact:
            reached = sorted((n for n in depth if n != origin), key=lambda n: (depth[n], n))
            selected = reached[:limit]
            result['dependents'] = [{'file': n, 'distance': depth[n], 'towardChangedFile': parent[n][0], 'evidenceEdge': parent[n][1]} for n in selected]
            result['discoveredDependents'] = len(reached)
            if len(reached) > limit:
                reasons.add('limit')
            involved.update(selected)
        else:
            found = target in depth
            path = [target] if found else []
            edges = []
            while found and path[-1] != origin:
                prev, edge = parent[path[-1]]
                path.append(prev)
                edges.append(edge)
            path.reverse()
            edges.reverse()
            result.update(found=found, path=path[:limit + 1], edges=edges[:limit], pathLength=len(edges) if found else None)
            if len(edges) > limit:
                reasons.add('limit')
            elif found:
                reasons.clear()  # One shortest path is sufficient; no all-path claim.
            involved.update(result['path'])
            result['meaning'] = 'One shortest candidate reference path' if found else 'No candidate path found within the inspected graph and bounds; dynamic calls may still exist'
        result['truncated'] = bool(reasons)
        result['truncationReasons'] = sorted(reasons)
    result['files'] = [{'id': n, 'layer': nodes[n].get('layer'), 'role': nodes[n].get('role')} for n in sorted(involved)]
    result['diagnostics'] = {}
    for key in ['unresolved', 'dynamic', 'parseErrors']:
        rows = data.get(key, [])
        relevant = [e for e in rows if e.get('source') in involved]
        result['diagnostics'][key] = {'globalCount': len(rows), 'relevantCount': len(relevant), 'items': relevant[:limit], 'truncated': len(relevant) > limit}
    result['coverage'] = {'inventoryOnlyCount': len(data.get('coverage', {}).get('inventoryOnly', [])),
                          'relevantInventoryOnly': [p for p in data.get('coverage', {}).get('inventoryOnly', []) if p in involved],
                          'reviewWarningCount': len(data.get('reviewWarnings', []))}
    result['limitations'] = ['File-level references and reviewed relations are not measured runtime calls.',
                            'No path does not prove absence of dynamic calls.',
                            'Impact lists candidate dependent files, not confirmed behavior changes or a complete test list; tests are excluded from the scanner inventory.']
    return result


def positive(value):
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError('must be positive')
    return n


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', '--project-root', dest='root', type=Path, required=True, help='Project root')
    parser.add_argument('--source-root', type=Path, help='Optional layer source directory inside project')
    parser.add_argument('--atlas', type=Path, help='default PROJECT/doc/architecture/atlas.json')
    select = parser.add_mutually_exclusive_group(required=True)
    select.add_argument('--file')
    select.add_argument('--from', dest='start')
    parser.add_argument('--to', dest='target')
    kind = parser.add_mutually_exclusive_group()
    kind.add_argument('--direction', choices=['dependencies', 'callers'])
    kind.add_argument('--impact', action='store_true')
    parser.add_argument('--max-depth', type=positive, default=20)
    parser.add_argument('--limit', type=positive, default=100)
    parser.add_argument('--max-nodes', type=positive, default=10000)
    args = parser.parse_args(argv)
    if args.start is not None and (args.target is None or args.direction or args.impact):
        parser.error('--from requires --to and cannot use --direction/--impact')
    if args.file is not None and args.target is not None:
        parser.error('--to requires --from')
    try:
        root, _ = sync.resolve_layout(args.root, args.source_root)
        atlas = args.atlas or root / 'doc/architecture/atlas.json'
        data = json.loads(atlas.read_text(encoding='utf-8'))
        validate(data)
        changed = freshness(data, root, args.source_root)
        if changed:
            print(sync.dump({'status': 'stale', 'changed': changed, 'action': 'Run sync_atlas.py with this source root and the directory containing this atlas.'}), end='')
            return 3
        result = query(data, args.file, args.direction or 'dependencies', args.impact, args.start, args.target, args.max_depth, args.limit, args.max_nodes)
        print(sync.dump({'status': 'current', 'sourceFingerprint': data['sourceFingerprint'], 'generatedAt': data['generatedAt'], **result}), end='')
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(sync.dump({'status': 'error', 'message': str(exc)}), end='')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
