"""assets.md: dataset commit, package versions, weight files with SHA-256, licences.

    python -m p1.assets --out results/P1-E01

Also holds the two licence checks of the brief's stop conditions.
"""
from __future__ import annotations

import argparse
import re
from importlib import metadata
from pathlib import Path

from . import data as D
from .common import git_commit, now_utc, sha256, write_json

TABPFN_REPO = "Prior-Labs/TabPFN-v2-reg"
TABICL_REPO = "jingang/TabICL"
ALLOWED_TABICL_LICENCES = ("bsd", "mit", "apache")
PACKAGES = ["tabpfn", "tabicl", "torch", "scikit-learn", "lightgbm", "optuna", "numpy", "pandas", "scipy",
            "joblib", "threadpoolctl", "matplotlib", "huggingface-hub"]


def _version(pkg: str) -> str:
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return "not installed"


def _package_licence(pkg: str) -> str:
    try:
        meta = metadata.metadata(pkg)
    except metadata.PackageNotFoundError:
        return "n/a"
    value = meta.get("License-Expression") or (meta.get("License") or "").strip().splitlines()[0:1]
    if isinstance(value, list):
        value = value[0] if value else ""
    if not value:
        value = "; ".join(c.split("::")[-1].strip() for c in meta.get_all("Classifier") or [] if "License" in c)
    return str(value)[:80] or "n/a"


def _card_licence(readme: Path) -> dict:
    """Licence fields of the YAML header of a Hugging Face model card."""
    text = readme.read_text(errors="replace")
    head = text.split("---")[1] if text.startswith("---") else ""
    out = {}
    for key in ("license", "license_name", "license_link"):
        m = re.search(rf"^{key}:\s*(.+)$", head, flags=re.M)
        if m:
            out[key] = m.group(1).strip().strip("'\"")
    return out


def tabpfn_weights() -> dict:
    """TabPFN v2 regressor weights. Downloaded without a token; fails if the repository is gated."""
    from huggingface_hub import hf_hub_download, model_info
    from tabpfn.model_loading import ModelSource, prepend_cache_path

    name = ModelSource.get_regressor_v2().default_filename
    path = Path(prepend_cache_path(name))
    if not path.exists():
        # The library's own download path for version V2; it involves no licence prompt.
        from tabpfn.constants import ModelVersion
        from tabpfn.model_loading import download_model

        result = download_model(path, version=ModelVersion.V2, which="regressor", model_name=name)
        if result != "ok":
            raise RuntimeError(f"TabPFN V2 weights could not be downloaded: {result}")
    info = model_info(TABPFN_REPO, token=False)
    licence_file = Path(hf_hub_download(TABPFN_REPO, "LICENSE.txt", token=False))
    card = _card_licence(Path(hf_hub_download(TABPFN_REPO, "README.md", token=False)))
    return dict(model="TabPFN v2 (regressor)", package=f"tabpfn=={_version('tabpfn')}", repo=TABPFN_REPO,
                repo_revision=info.sha, gated=bool(info.gated), file=name, path=str(path), bytes=path.stat().st_size,
                sha256=sha256(path), licence=card, licence_file=str(licence_file),
                licence_text=licence_file.read_text(errors="replace"))


def tabicl_weights() -> dict:
    """TabICLv2 regressor weights: the default checkpoint of the installed package."""
    import inspect

    from huggingface_hub import hf_hub_download, model_info
    from tabicl import TabICLRegressor

    name = inspect.signature(TabICLRegressor.__init__).parameters["checkpoint_version"].default
    path = Path(hf_hub_download(TABICL_REPO, name, token=False))
    info = model_info(TABICL_REPO, token=False)
    card = _card_licence(Path(hf_hub_download(TABICL_REPO, "README.md", token=False)))
    licence = (card.get("license") or "").lower()
    return dict(model="TabICLv2 (regressor)", package=f"tabicl=={_version('tabicl')}", repo=TABICL_REPO,
                repo_revision=info.sha, gated=bool(info.gated), file=name, path=str(path), bytes=path.stat().st_size,
                sha256=sha256(path), licence=card, package_licence=_package_licence("tabicl"),
                licence_allowed=any(licence.startswith(a) for a in ALLOWED_TABICL_LICENCES))


def write_assets(out: str | Path, data_root: str = D.DEFAULT_ROOT) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    pfn, icl = tabpfn_weights(), tabicl_weights()
    (out / "licences").mkdir(exist_ok=True)
    (out / "licences" / "TabPFN-v2-reg_LICENSE.txt").write_text(pfn.pop("licence_text"))
    record = dict(written_utc=now_utc(), dataset=dict(url=D.DATASET_URL, commit=git_commit(data_root)),
                  tabpfn=pfn, tabicl=icl, packages={p: _version(p) for p in PACKAGES})
    write_json(out / "config" / "assets.json", record)

    L = ["# Assets used by P1-E01\n", f"Written {record['written_utc']}. Machine-readable copy: `config/assets.json`.\n",
         "## Dataset\n",
         "| Item | Value |", "|---|---|",
         "| Name | SODIndoorLoc |",
         f"| Source | {D.DATASET_URL} |",
         f"| Version | commit `{record['dataset']['commit']}` |",
         "| Licence | No licence file in the repository. Its README asks for a citation of Bi et al., "
         "Satellite Navigation 3:25 (2022). |",
         "| Files used | the training and test CSV files of the five configurations in `briefs/P1-E01.md`; "
         "the `_Avg` files are not used |\n",
         "## Model weights\n",
         "| Model | Package | Source | Revision | File | Bytes | SHA-256 | Licence |", "|---|---|---|---|---|---|---|---|"]
    for w, lic in ((pfn, f"{pfn['licence'].get('license_name') or pfn['licence'].get('license')} "
                              "(text in `licences/TabPFN-v2-reg_LICENSE.txt`, shipped with the weights)"),
                   (icl, f"{icl['licence'].get('license')} (model card); package licence: {icl['package_licence']}")):
        L.append(f"| {w['model']} | `{w['package']}` | huggingface.co/{w['repo']} | `{w['repo_revision']}` | "
                 f"`{w['file']}` | {w['bytes']:,} | `{w['sha256']}` | {lic} |")
    L += ["", f"Neither repository is gated (TabPFN: gated={pfn['gated']}; TabICL: gated={icl['gated']}). Both were "
              "downloaded without a token, an account or a licence prompt.\n",
          "## Packages\n", "| Package | Version | Licence (package metadata) |", "|---|---|---|"]
    for p in PACKAGES:
        L.append(f"| {p} | {_version(p)} | {_package_licence(p)} |")
    L.append("\nThe full package list is in `env.txt`.")
    (out / "assets.md").write_text("\n".join(L) + "\n")
    return record


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/P1-E01")
    ap.add_argument("--data", default=D.DEFAULT_ROOT)
    a = ap.parse_args()
    rec = write_assets(a.out, a.data)
    print(f"tabpfn: {rec['tabpfn']['file']} sha256={rec['tabpfn']['sha256']} licence={rec['tabpfn']['licence']}")
    print(f"tabicl: {rec['tabicl']['file']} sha256={rec['tabicl']['sha256']} licence={rec['tabicl']['licence']} "
          f"allowed={rec['tabicl']['licence_allowed']}")
