# Assets used by P1-E01

Written 2026-11-14T23:50:45Z. Machine-readable copy: `config/assets.json`.

## Dataset

| Item | Value |
|---|---|
| Name | SODIndoorLoc |
| Source | https://github.com/bijingxue/SODIndoorLoc |
| Version | commit `bfe8f63f55957cc25b23ba91c408ae345a3fb0b7` |
| Licence | No licence file in the repository. Its README asks for a citation of Bi et al., Satellite Navigation 3:25 (2022). |
| Files used | the training and test CSV files of the five configurations in `briefs/P1-E01.md`; the `_Avg` files are not used |

## Model weights

| Model | Package | Source | Revision | File | Bytes | SHA-256 | Licence |
|---|---|---|---|---|---|---|---|
| TabPFN v2 (regressor) | `tabpfn==10.0.0` | huggingface.co/Prior-Labs/TabPFN-v2-reg | `02a44705ff7790b50cded404bc59adb94da456a1` | `tabpfn-v2-regressor.ckpt` | 44,390,977 | `2ab5a07d5c41dfe6db9aa7ae106fc6de898326c2765be66505a07e2868c10736` | priorlabs-1-1 (text in `licences/TabPFN-v2-reg_LICENSE.txt`, shipped with the weights) |
| TabICLv2 (regressor) | `tabicl==2.2.0` | huggingface.co/jingang/TabICL | `4dcd344ece2c00be9e831fdd35bed57b5ad83e19` | `tabicl-regressor-v2-20260212.ckpt` | 114,324,594 | `0db9cb538f114e79026bf08f45f41ad8dd7ad2de2aaca9a5ca8cd3bd9748ae7a` | bsd-3-clause (model card); package licence: BSD 3-Clause License |

Neither repository is gated (TabPFN: gated=False; TabICL: gated=False). Both were downloaded without a token, an account or a licence prompt.

## Packages

| Package | Version | Licence (package metadata) |
|---|---|---|
| tabpfn | 10.0.0 | Apache-2.0 |
| tabicl | 2.2.0 | BSD 3-Clause License |
| torch | 2.15.0 | Apache-2.0 AND Apache-2.0 WITH LLVM-exception AND BSD-2-Clause AND BSD-3-Clause  |
| scikit-learn | 1.9.1 | BSD-3-Clause |
| lightgbm | 4.7.0 | MIT |
| optuna | 5.0.0 | MIT License |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| pandas | 3.1.1 | BSD-3-Clause |
| scipy | 1.18.1 | Copyright (c) 2001-2002 Enthought, Inc. 2003, SciPy Developers. |
| joblib | 1.6.0 | BSD-3-Clause |
| threadpoolctl | 3.8.0 | BSD-3-Clause |
| matplotlib | 3.11.2 | License agreement for matplotlib versions 1.3.0 and later |
| huggingface-hub | 2.4.0 | Apache-2.0 |

The full package list is in `env.txt`.
