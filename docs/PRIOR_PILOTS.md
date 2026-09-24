# Prior pre-registered pilots (both NO-GO)

## GeoRoute — routing subject-specific LoRA adapters by covariance distance
Criterion: routed merge/ensemble beats uniform AND random by >= 1 pp (p < .05) and Spearman(distance, transfer) >= 0.2.
| Dataset | GeoRoute | Uniform | Random | Spearman |
|---|---|---|---|---|
| BCI IV-2a (merge, jobs 010/020/021) | 59.3 | 58.9 | 58.3 | 0.18 |
| Lee2019 (merge, job 031, 54 subj) | 75.5 | 75.6 | 75.4 | -0.01 |
| Lee2019 (output ensemble) | 75.6 | 75.5 | 75.5 | -0.01 |

## RCTTA — Riemannian co-training test-time adaptation (jobs 040/041)
Criterion: rctta or rctta+t3a beats each of T3A, LAME, Tent by >= 1.5 pp with >= 6/9 wins (CBraMod).
Result: rctta+t3a 64.0 vs T3A 63.5 (+0.42 pp, 5/9 wins) -> NO-GO.
