import yaml

def load_level_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_ascii_map(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]
    spawns = {'sink': None, 'med_cart': None, 'patient': None, 'player': None}
    doors = []
    for r, row in enumerate(lines):
        for c, ch in enumerate(row):
            if ch == 'S': spawns['sink']     = (c, r)
            if ch == 'C': spawns['med_cart'] = (c, r)
            if ch == 'P': spawns['patient']  = (c, r)
            if ch == 'J': spawns['player'] = (c, r)
            if ch == 'D': doors.append((c, r))
    return {'grid': lines, 'spawns': spawns, 'doors': doors}
