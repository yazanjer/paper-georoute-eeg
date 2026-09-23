# Summary

| dataset      | method              |   acc_mean |   acc_sd_subjects |   acc_sd_seeds |   kappa_mean |   n_subjects |   n_seeds |
|:-------------|:--------------------|-----------:|------------------:|---------------:|-------------:|-------------:|----------:|
| bnci2014_001 | georoute+t3a        |     0.6404 |            0.1561 |            nan |       0.5206 |            9 |         1 |
| bnci2014_001 | shared_only+t3a     |     0.6370 |            0.1548 |            nan |       0.5159 |            9 |         1 |
| bnci2014_001 | eegnet_ea           |     0.6346 |            0.1587 |            nan |       0.5129 |            9 |         1 |
| bnci2014_001 | oracle_best_single  |     0.6096 |            0.1399 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | cbramod_fullft_ea   |     0.6003 |            0.1348 |            nan |       0.4671 |            9 |         1 |
| bnci2014_001 | georoute[logeuclid] |     0.5941 |            0.1452 |            nan |       0.4588 |            9 |         1 |
| bnci2014_001 | georoute            |     0.5934 |            0.1451 |            nan |       0.4578 |            9 |         1 |
| bnci2014_001 | georoute[top3]      |     0.5934 |            0.1451 |            nan |       0.4578 |            9 |         1 |
| bnci2014_001 | georoute@n20        |     0.5922 |            0.1479 |            nan |       0.4563 |            9 |         1 |
| bnci2014_001 | georoute@n50        |     0.5922 |            0.1502 |            nan |       0.4563 |            9 |         1 |
| bnci2014_001 | georoute@n10        |     0.5914 |            0.1461 |            nan |       0.4552 |            9 |         1 |
| bnci2014_001 | georoute[top5]      |     0.5910 |            0.1479 |            nan |       0.4547 |            9 |         1 |
| bnci2014_001 | georoute[top8]      |     0.5910 |            0.1455 |            nan |       0.4547 |            9 |         1 |
| bnci2014_001 | eegnet              |     0.5903 |            0.1014 |            nan |       0.4537 |            9 |         1 |
| bnci2014_001 | uniform_merge       |     0.5891 |            0.1453 |            nan |       0.4522 |            9 |         1 |
| bnci2014_001 | georoute[feature]   |     0.5883 |            0.1483 |            nan |       0.4511 |            9 |         1 |
| bnci2014_001 | shared_only         |     0.5876 |            0.1400 |            nan |       0.4501 |            9 |         1 |
| bnci2014_001 | georoute[top1]      |     0.5841 |            0.1641 |            nan |       0.4455 |            9 |         1 |
| bnci2014_001 | random_route        |     0.5833 |            0.1436 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | georoute[euclid]    |     0.5787 |            0.1368 |            nan |       0.4383 |            9 |         1 |
| bnci2014_001 | georoute@n5         |     0.5783 |            0.1377 |            nan |       0.4378 |            9 |         1 |
| bnci2014_001 | conformer_ea        |     0.5706 |            0.1392 |            nan |       0.4275 |            9 |         1 |
| bnci2014_001 | shallow_ea          |     0.5694 |            0.1379 |            nan |       0.4259 |            9 |         1 |
| bnci2014_001 | ts_lr_ra            |     0.4491 |            0.1310 |            nan |       0.2654 |            9 |         1 |
| bnci2014_001 | cbramod_lp_ea       |     0.4321 |            0.1164 |            nan |       0.2428 |            9 |         1 |
| bnci2014_001 | csp_lda_ea          |     0.4294 |            0.1463 |            nan |       0.2392 |            9 |         1 |
| bnci2014_001 | mdm_ra              |     0.4124 |            0.1293 |            nan |       0.2166 |            9 |         1 |

## Paired tests vs georoute

| dataset      | ref      | vs                  |   mean_diff |      p |   rank_biserial |   wins |   ties |   losses |   n |   p_holm |
|:-------------|:---------|:--------------------|------------:|-------:|----------------:|-------:|-------:|---------:|----:|---------:|
| bnci2014_001 | georoute | cbramod_fullft_ea   |     -0.0069 | 0.5156 |         -0.2667 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | cbramod_lp_ea       |      0.1613 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.1016 |
| bnci2014_001 | georoute | conformer_ea        |      0.0228 | 0.2109 |          0.4889 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | csp_lda_ea          |      0.1640 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.1016 |
| bnci2014_001 | georoute | eegnet              |      0.0031 | 1.0000 |          0.0222 |      5 |      0 |        4 |   9 |   1.0000 |
| bnci2014_001 | georoute | eegnet_ea           |     -0.0413 | 0.0977 |         -0.6444 |      3 |      0 |        6 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute+t3a        |     -0.0471 | 0.0039 |         -1.0000 |      0 |      0 |        9 |   9 |   0.1016 |
| bnci2014_001 | georoute | georoute@n10        |      0.0019 | 0.6680 |          0.1778 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n20        |      0.0012 | 0.8438 |          0.0889 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n5         |      0.0150 | 0.8438 |          0.0889 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n50        |      0.0012 | 0.8047 |          0.1111 |      4 |      1 |        4 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[euclid]    |      0.0147 | 0.4609 |          0.3333 |      5 |      1 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[feature]   |      0.0050 | 0.4141 |          0.3611 |      5 |      1 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[logeuclid] |     -0.0008 | 1.0000 |         -1.0000 |      0 |      8 |        1 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top1]      |      0.0093 | 0.4961 |          0.2889 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top3]      |      0.0000 | 1.0000 |          0.0000 |      0 |      9 |        0 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top5]      |      0.0023 | 0.5469 |          0.2857 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top8]      |      0.0023 | 0.6719 |          0.1944 |      4 |      1 |        4 |   9 |   1.0000 |
| bnci2014_001 | georoute | mdm_ra              |      0.1809 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.1016 |
| bnci2014_001 | georoute | oracle_best_single  |     -0.0162 | 0.1289 |         -0.6000 |      1 |      0 |        8 |   9 |   1.0000 |
| bnci2014_001 | georoute | random_route        |      0.0101 | 0.3008 |          0.4222 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | shallow_ea          |      0.0239 | 0.1289 |          0.6000 |      7 |      0 |        2 |   9 |   1.0000 |
| bnci2014_001 | georoute | shared_only         |      0.0058 | 1.0000 |         -0.0222 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | shared_only+t3a     |     -0.0436 | 0.0117 |         -0.9111 |      1 |      0 |        8 |   9 |   0.2461 |
| bnci2014_001 | georoute | ts_lr_ra            |      0.1443 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.1016 |
| bnci2014_001 | georoute | uniform_merge       |      0.0042 | 0.7812 |          0.1429 |      4 |      2 |        3 |   9 |   1.0000 |

## Distance -> transfer Spearman (mean over subjects/seeds)

|                               |   mean |   std |   count |
|:------------------------------|-------:|------:|--------:|
| ('bnci2014_001', 'euclid')    |  0.134 | 0.282 |   9.000 |
| ('bnci2014_001', 'feature')   |  0.214 | 0.324 |   9.000 |
| ('bnci2014_001', 'logeuclid') |  0.179 | 0.244 |   9.000 |
| ('bnci2014_001', 'riemann')   |  0.181 | 0.227 |   9.000 |