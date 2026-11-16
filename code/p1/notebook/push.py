"""Write the script that puts the P1-E01 cells into a node's live marimo notebook.

    python code/p1/notebook/push.py --node nodeA --configs HCXY-All --commit <sha> \
        --workers 3 --threads 6 [--only workspace launch] [--no-run] > push_nodeA.py

The printed script is then executed in the notebook's kernel through the pair
channel. It creates each cell by name, or replaces the cell of that name, and
runs it. Cells are created with marimo's code-mode API, never by editing the
notebook file.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

TEMPLATE = '''
import base64, json
import marimo._code_mode as cm

_specs = json.loads(base64.b64decode("{payload}").decode())
async with cm.get_context(skip_staleness_check=True) as ctx:
    _by_name = {{c.name: c.id for c in ctx.cells if getattr(c, "name", None)}}
    for _s in _specs:
        if _s["name"] in _by_name:
            _cid = _by_name[_s["name"]]
            ctx.edit_cell(_cid, _s["code"])
            print("edited ", _s["name"], _cid)
        else:
            _cid = ctx.create_cell(_s["code"], name=_s["name"], hide_code=_s["hide"])
            print("created", _s["name"], _cid)
        if _s["run"]:
            ctx.run_cell(_cid)
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default="e01", choices=["e01", "e02", "e03"])
    ap.add_argument("--node", required=True)
    ap.add_argument("--configs", nargs="*", default=[])
    ap.add_argument("--commit", required=True)
    ap.add_argument("--commit-cpu", default=None, help="e02: commit of the CPU job's checkout")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--only", nargs="*", default=None, help="send only the cells with these names")
    ap.add_argument("--no-run", action="store_true", help="create or edit the cells without running them")
    ap.add_argument("--helpers", default=None, help="file with the notebook helper cell (sent first, hidden)")
    ap.add_argument("--draws", nargs="*", type=int, default=[], help="e02: Part A draws of this node")
    ap.add_argument("--extra-draws", nargs="*", type=int, default=[], help="e02: draws moved here from another node")
    ap.add_argument("--extra-configs", nargs="*", default=[], help="e03: part C configurations moved here")
    ap.add_argument("--own", nargs="*", default=[], help="e02: configurations whose P1-E01 results are on this node")
    a = ap.parse_args()
    if a.brief == "e01":
        from p1.notebook.cells_e01 import cells

        specs = cells(a.node, a.configs, a.commit, a.workers, a.threads)
    elif a.brief == "e02":
        from p1.notebook.cells_e02 import cells

        specs = cells(a.node, a.draws, a.own, a.commit, a.workers, a.threads, commit_cpu=a.commit_cpu,
                      extra_draws=a.extra_draws)
    else:
        from p1.notebook.cells_e03 import cells

        specs = cells(a.node, a.configs, a.own, a.commit, extra_configs=a.extra_configs)
    if a.helpers:
        specs.insert(2, dict(name="helpers", code=Path(a.helpers).read_text(), hide=True, run=True))
    if a.only is not None:
        specs = [s for s in specs if s["name"] in a.only]
    if a.no_run:
        specs = [dict(s, run=False) for s in specs]
    payload = base64.b64encode(json.dumps(specs).encode()).decode()
    print(TEMPLATE.format(payload=payload))


if __name__ == "__main__":
    main()
