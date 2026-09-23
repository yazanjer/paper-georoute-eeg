# Summary

| dataset      | method                        |   acc_mean |   acc_sd_subjects |   acc_sd_seeds |   kappa_mean |   n_subjects |   n_seeds |
|:-------------|:------------------------------|-----------:|------------------:|---------------:|-------------:|-------------:|----------:|
| bnci2014_001 | georoute+t3a_shres            |     0.6412 |            0.1596 |            nan |       0.5216 |            9 |         1 |
| bnci2014_001 | georoute+t3a                  |     0.6404 |            0.1561 |            nan |       0.5206 |            9 |         1 |
| bnci2014_001 | shared_only+t3a               |     0.6370 |            0.1548 |            nan |       0.5159 |            9 |         1 |
| bnci2014_001 | shared_only+t3a_shind         |     0.6370 |            0.1548 |            nan |       0.5159 |            9 |         1 |
| bnci2014_001 | shared_only+t3a_shres         |     0.6370 |            0.1548 |            nan |       0.5159 |            9 |         1 |
| bnci2014_001 | eegnet_ea                     |     0.6346 |            0.1587 |            nan |       0.5129 |            9 |         1 |
| bnci2014_001 | georoute+t3a_shind            |     0.6142 |            0.1587 |            nan |       0.4856 |            9 |         1 |
| bnci2014_001 | oracle_best_expert_shres      |     0.6123 |            0.1378 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | oracle_best_single_shres      |     0.6119 |            0.1362 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | oracle_best_single            |     0.6096 |            0.1399 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | cbramod_fullft_ea             |     0.6003 |            0.1348 |            nan |       0.4671 |            9 |         1 |
| bnci2014_001 | georoute[logeuclid]           |     0.5941 |            0.1452 |            nan |       0.4588 |            9 |         1 |
| bnci2014_001 | georoute[euclid]_shres        |     0.5938 |            0.1438 |            nan |       0.4583 |            9 |         1 |
| bnci2014_001 | georoute                      |     0.5934 |            0.1451 |            nan |       0.4578 |            9 |         1 |
| bnci2014_001 | georoute[top3]                |     0.5934 |            0.1451 |            nan |       0.4578 |            9 |         1 |
| bnci2014_001 | georoute@n20                  |     0.5922 |            0.1479 |            nan |       0.4563 |            9 |         1 |
| bnci2014_001 | georoute@n50                  |     0.5922 |            0.1502 |            nan |       0.4563 |            9 |         1 |
| bnci2014_001 | oracle_best_single_shind      |     0.5918 |            0.1417 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | georoute@n10                  |     0.5914 |            0.1461 |            nan |       0.4552 |            9 |         1 |
| bnci2014_001 | georoute[top5]                |     0.5910 |            0.1479 |            nan |       0.4547 |            9 |         1 |
| bnci2014_001 | georoute[top5]_shres          |     0.5910 |            0.1414 |            nan |       0.4547 |            9 |         1 |
| bnci2014_001 | georoute[top8]                |     0.5910 |            0.1455 |            nan |       0.4547 |            9 |         1 |
| bnci2014_001 | eegnet                        |     0.5903 |            0.1014 |            nan |       0.4537 |            9 |         1 |
| bnci2014_001 | georoute[logeuclid]_shres     |     0.5899 |            0.1499 |            nan |       0.4532 |            9 |         1 |
| bnci2014_001 | georoute[top8]_shres          |     0.5895 |            0.1409 |            nan |       0.4527 |            9 |         1 |
| bnci2014_001 | georoute[feature]_shres       |     0.5895 |            0.1444 |            nan |       0.4527 |            9 |         1 |
| bnci2014_001 | georoute[top3]_shres          |     0.5895 |            0.1510 |            nan |       0.4527 |            9 |         1 |
| bnci2014_001 | georoute_shres                |     0.5895 |            0.1510 |            nan |       0.4527 |            9 |         1 |
| bnci2014_001 | uniform_merge                 |     0.5891 |            0.1453 |            nan |       0.4522 |            9 |         1 |
| bnci2014_001 | uniform_merge_shres           |     0.5891 |            0.1422 |            nan |       0.4522 |            9 |         1 |
| bnci2014_001 | georoute[feature]             |     0.5883 |            0.1483 |            nan |       0.4511 |            9 |         1 |
| bnci2014_001 | georoute_ens[top5]_shres      |     0.5883 |            0.1561 |            nan |       0.4511 |            9 |         1 |
| bnci2014_001 | random_route_shres            |     0.5881 |            0.1441 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | shared_only                   |     0.5876 |            0.1400 |            nan |       0.4501 |            9 |         1 |
| bnci2014_001 | georoute_ens[top8]_shres      |     0.5872 |            0.1546 |            nan |       0.4496 |            9 |         1 |
| bnci2014_001 | shared_only_shind             |     0.5868 |            0.1403 |            nan |       0.4491 |            9 |         1 |
| bnci2014_001 | shared_only_shres             |     0.5868 |            0.1403 |            nan |       0.4491 |            9 |         1 |
| bnci2014_001 | georoute[top1]_shres          |     0.5864 |            0.1279 |            nan |       0.4486 |            9 |         1 |
| bnci2014_001 | uniform_ens_shres             |     0.5849 |            0.1523 |            nan |       0.4465 |            9 |         1 |
| bnci2014_001 | georoute[top1]                |     0.5841 |            0.1641 |            nan |       0.4455 |            9 |         1 |
| bnci2014_001 | random_route                  |     0.5833 |            0.1436 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | georoute@n10_shres            |     0.5829 |            0.1360 |            nan |       0.4439 |            9 |         1 |
| bnci2014_001 | georoute_ens[top3]_shres      |     0.5822 |            0.1600 |            nan |       0.4429 |            9 |         1 |
| bnci2014_001 | georoute_ens_shres            |     0.5822 |            0.1600 |            nan |       0.4429 |            9 |         1 |
| bnci2014_001 | georoute_ens[logeuclid]_shres |     0.5822 |            0.1601 |            nan |       0.4429 |            9 |         1 |
| bnci2014_001 | georoute[euclid]              |     0.5787 |            0.1368 |            nan |       0.4383 |            9 |         1 |
| bnci2014_001 | georoute@n5                   |     0.5783 |            0.1377 |            nan |       0.4378 |            9 |         1 |
| bnci2014_001 | georoute[top8]_shind          |     0.5741 |            0.1454 |            nan |       0.4321 |            9 |         1 |
| bnci2014_001 | random_ens_shres              |     0.5738 |            0.1495 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | georoute_ens[feature]_shres   |     0.5729 |            0.1526 |            nan |       0.4306 |            9 |         1 |
| bnci2014_001 | georoute[logeuclid]_shind     |     0.5710 |            0.1439 |            nan |       0.4280 |            9 |         1 |
| bnci2014_001 | uniform_merge_shind           |     0.5710 |            0.1442 |            nan |       0.4280 |            9 |         1 |
| bnci2014_001 | conformer_ea                  |     0.5706 |            0.1392 |            nan |       0.4275 |            9 |         1 |
| bnci2014_001 | random_route_shind            |     0.5699 |            0.1450 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | georoute[top3]_shind          |     0.5698 |            0.1434 |            nan |       0.4264 |            9 |         1 |
| bnci2014_001 | georoute_shind                |     0.5698 |            0.1434 |            nan |       0.4264 |            9 |         1 |
| bnci2014_001 | georoute[top5]_shind          |     0.5698 |            0.1494 |            nan |       0.4264 |            9 |         1 |
| bnci2014_001 | shallow_ea                    |     0.5694 |            0.1379 |            nan |       0.4259 |            9 |         1 |
| bnci2014_001 | georoute@n10_shind            |     0.5683 |            0.1343 |            nan |       0.4244 |            9 |         1 |
| bnci2014_001 | georoute_ens@n10_shres        |     0.5679 |            0.1478 |            nan |       0.4239 |            9 |         1 |
| bnci2014_001 | georoute[euclid]_shind        |     0.5675 |            0.1419 |            nan |       0.4234 |            9 |         1 |
| bnci2014_001 | georoute[top1]_shind          |     0.5652 |            0.1411 |            nan |       0.4203 |            9 |         1 |
| bnci2014_001 | georoute[feature]_shind       |     0.5637 |            0.1523 |            nan |       0.4182 |            9 |         1 |
| bnci2014_001 | georoute_ens[euclid]_shres    |     0.5540 |            0.1462 |            nan |       0.4053 |            9 |         1 |
| bnci2014_001 | georoute_ens[top1]_shres      |     0.5540 |            0.1604 |            nan |       0.4053 |            9 |         1 |
| bnci2014_001 | oracle_best_expert_shind      |     0.5440 |            0.1389 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | uniform_ens_shind             |     0.5231 |            0.1493 |            nan |       0.3642 |            9 |         1 |
| bnci2014_001 | georoute_ens[top8]_shind      |     0.5197 |            0.1636 |            nan |       0.3596 |            9 |         1 |
| bnci2014_001 | georoute_ens[top5]_shind      |     0.4988 |            0.1668 |            nan |       0.3318 |            9 |         1 |
| bnci2014_001 | georoute_ens[logeuclid]_shind |     0.4877 |            0.1789 |            nan |       0.3169 |            9 |         1 |
| bnci2014_001 | georoute_ens[top3]_shind      |     0.4869 |            0.1789 |            nan |       0.3158 |            9 |         1 |
| bnci2014_001 | georoute_ens_shind            |     0.4869 |            0.1789 |            nan |       0.3158 |            9 |         1 |
| bnci2014_001 | georoute_ens[feature]_shind   |     0.4799 |            0.1623 |            nan |       0.3066 |            9 |         1 |
| bnci2014_001 | georoute_ens@n10_shind        |     0.4695 |            0.1340 |            nan |       0.2927 |            9 |         1 |
| bnci2014_001 | georoute_ens[top1]_shind      |     0.4560 |            0.1972 |            nan |       0.2747 |            9 |         1 |
| bnci2014_001 | ts_lr_ra                      |     0.4491 |            0.1310 |            nan |       0.2654 |            9 |         1 |
| bnci2014_001 | random_ens_shind              |     0.4475 |            0.1270 |            nan |     nan      |            9 |         1 |
| bnci2014_001 | georoute_ens[euclid]_shind    |     0.4379 |            0.1327 |            nan |       0.2505 |            9 |         1 |
| bnci2014_001 | cbramod_lp_ea                 |     0.4321 |            0.1164 |            nan |       0.2428 |            9 |         1 |
| bnci2014_001 | csp_lda_ea                    |     0.4294 |            0.1463 |            nan |       0.2392 |            9 |         1 |
| bnci2014_001 | mdm_ra                        |     0.4124 |            0.1293 |            nan |       0.2166 |            9 |         1 |

## Paired tests vs georoute

| dataset      | ref      | vs                            |   mean_diff |      p |   rank_biserial |   wins |   ties |   losses |   n |   p_holm |
|:-------------|:---------|:------------------------------|------------:|-------:|----------------:|-------:|-------:|---------:|----:|---------:|
| bnci2014_001 | georoute | cbramod_fullft_ea             |     -0.0069 | 0.5156 |         -0.2667 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | cbramod_lp_ea                 |      0.1613 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | conformer_ea                  |      0.0228 | 0.2109 |          0.4889 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | csp_lda_ea                    |      0.1640 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | eegnet                        |      0.0031 | 1.0000 |          0.0222 |      5 |      0 |        4 |   9 |   1.0000 |
| bnci2014_001 | georoute | eegnet_ea                     |     -0.0413 | 0.0977 |         -0.6444 |      3 |      0 |        6 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute+t3a                  |     -0.0471 | 0.0039 |         -1.0000 |      0 |      0 |        9 |   9 |   0.3125 |
| bnci2014_001 | georoute | georoute+t3a_shind            |     -0.0208 | 0.3008 |         -0.4222 |      3 |      0 |        6 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute+t3a_shres            |     -0.0478 | 0.0195 |         -0.8667 |      2 |      0 |        7 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n10                  |      0.0019 | 0.6680 |          0.1778 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n10_shind            |      0.0251 | 0.1758 |          0.5333 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n10_shres            |      0.0104 | 0.5703 |          0.2444 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n20                  |      0.0012 | 0.8438 |          0.0889 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n5                   |      0.0150 | 0.8438 |          0.0889 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute@n50                  |      0.0012 | 0.8047 |          0.1111 |      4 |      1 |        4 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[euclid]              |      0.0147 | 0.4609 |          0.3333 |      5 |      1 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[euclid]_shind        |      0.0258 | 0.0508 |          0.7333 |      8 |      0 |        1 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[euclid]_shres        |     -0.0004 | 0.5469 |         -0.2857 |      2 |      2 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[feature]             |      0.0050 | 0.4141 |          0.3611 |      5 |      1 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[feature]_shind       |      0.0297 | 0.0742 |          0.6889 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[feature]_shres       |      0.0039 | 0.8438 |          0.1071 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[logeuclid]           |     -0.0008 | 1.0000 |         -1.0000 |      0 |      8 |        1 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[logeuclid]_shind     |      0.0224 | 0.1953 |          0.5111 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[logeuclid]_shres     |      0.0035 | 0.6094 |          0.2500 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top1]                |      0.0093 | 0.4961 |          0.2889 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top1]_shind          |      0.0282 | 0.0742 |          0.6889 |      8 |      0 |        1 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top1]_shres          |      0.0069 | 0.4688 |          0.3571 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top3]                |      0.0000 | 1.0000 |          0.0000 |      0 |      9 |        0 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top3]_shind          |      0.0235 | 0.1602 |          0.5556 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top3]_shres          |      0.0039 | 0.6094 |          0.2500 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top5]                |      0.0023 | 0.5469 |          0.2857 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top5]_shind          |      0.0235 | 0.1953 |          0.5556 |      5 |      1 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top5]_shres          |      0.0023 | 0.8438 |         -0.1071 |      3 |      2 |        4 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top8]                |      0.0023 | 0.6719 |          0.1944 |      4 |      1 |        4 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top8]_shind          |      0.0193 | 0.2617 |          0.4444 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute[top8]_shres          |      0.0039 | 0.9531 |         -0.0714 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens@n10_shind        |      0.1238 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | georoute_ens@n10_shres        |      0.0255 | 0.0938 |          0.6444 |      7 |      0 |        2 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens[euclid]_shind    |      0.1555 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | georoute_ens[euclid]_shres    |      0.0394 | 0.0195 |          0.8667 |      8 |      0 |        1 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens[feature]_shind   |      0.1134 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | georoute_ens[feature]_shres   |      0.0204 | 0.1016 |          0.6222 |      7 |      0 |        2 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens[logeuclid]_shind |      0.1057 | 0.0078 |          0.9556 |      8 |      0 |        1 |   9 |   0.5312 |
| bnci2014_001 | georoute | georoute_ens[logeuclid]_shres |      0.0112 | 0.2383 |          0.4667 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens[top1]_shind      |      0.1373 | 0.0117 |          0.9111 |      8 |      0 |        1 |   9 |   0.7617 |
| bnci2014_001 | georoute | georoute_ens[top1]_shres      |      0.0394 | 0.0195 |          0.8667 |      7 |      0 |        2 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens[top3]_shind      |      0.1065 | 0.0078 |          0.9556 |      8 |      0 |        1 |   9 |   0.5312 |
| bnci2014_001 | georoute | georoute_ens[top3]_shres      |      0.0112 | 0.2344 |          0.5000 |      6 |      1 |        2 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens[top5]_shind      |      0.0945 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | georoute_ens[top5]_shres      |      0.0050 | 0.6289 |          0.2000 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens[top8]_shind      |      0.0737 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | georoute_ens[top8]_shres      |      0.0062 | 0.4219 |          0.3333 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_ens_shind            |      0.1065 | 0.0078 |          0.9556 |      8 |      0 |        1 |   9 |   0.5312 |
| bnci2014_001 | georoute | georoute_ens_shres            |      0.0112 | 0.2344 |          0.5000 |      6 |      1 |        2 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_shind                |      0.0235 | 0.1602 |          0.5556 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | georoute_shres                |      0.0039 | 0.6094 |          0.2500 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | mdm_ra                        |      0.1809 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | oracle_best_expert_shind      |      0.0494 | 0.0195 |          0.8667 |      8 |      0 |        1 |   9 |   1.0000 |
| bnci2014_001 | georoute | oracle_best_expert_shres      |     -0.0189 | 0.2188 |         -0.6190 |      1 |      3 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | oracle_best_single            |     -0.0162 | 0.1289 |         -0.6000 |      1 |      0 |        8 |   9 |   1.0000 |
| bnci2014_001 | georoute | oracle_best_single_shind      |      0.0015 | 0.8867 |         -0.0667 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | oracle_best_single_shres      |     -0.0185 | 0.0977 |         -0.6444 |      1 |      0 |        8 |   9 |   1.0000 |
| bnci2014_001 | georoute | random_ens_shind              |      0.1459 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | random_ens_shres              |      0.0195 | 0.0391 |          0.7778 |      7 |      0 |        2 |   9 |   1.0000 |
| bnci2014_001 | georoute | random_route                  |      0.0101 | 0.3008 |          0.4222 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | random_route_shind            |      0.0235 | 0.2500 |          0.4667 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | random_route_shres            |      0.0052 | 0.6406 |          0.2222 |      4 |      1 |        4 |   9 |   1.0000 |
| bnci2014_001 | georoute | shallow_ea                    |      0.0239 | 0.1289 |          0.6000 |      7 |      0 |        2 |   9 |   1.0000 |
| bnci2014_001 | georoute | shared_only                   |      0.0058 | 1.0000 |         -0.0222 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | shared_only+t3a               |     -0.0436 | 0.0117 |         -0.9111 |      1 |      0 |        8 |   9 |   0.7617 |
| bnci2014_001 | georoute | shared_only+t3a_shind         |     -0.0436 | 0.0117 |         -0.9111 |      1 |      0 |        8 |   9 |   0.7617 |
| bnci2014_001 | georoute | shared_only+t3a_shres         |     -0.0436 | 0.0117 |         -0.9111 |      1 |      0 |        8 |   9 |   0.7617 |
| bnci2014_001 | georoute | shared_only_shind             |      0.0066 | 1.0000 |          0.0000 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | shared_only_shres             |      0.0066 | 1.0000 |          0.0000 |      4 |      0 |        5 |   9 |   1.0000 |
| bnci2014_001 | georoute | ts_lr_ra                      |      0.1443 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | uniform_ens_shind             |      0.0702 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.3125 |
| bnci2014_001 | georoute | uniform_ens_shres             |      0.0085 | 0.4766 |          0.2889 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | uniform_merge                 |      0.0042 | 0.7812 |          0.1429 |      4 |      2 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | uniform_merge_shind           |      0.0224 | 0.1211 |          0.6000 |      6 |      0 |        3 |   9 |   1.0000 |
| bnci2014_001 | georoute | uniform_merge_shres           |      0.0042 | 0.8438 |         -0.1071 |      3 |      2 |        4 |   9 |   1.0000 |

## Distance -> transfer Spearman (mean over subjects/seeds)

|                                         |   mean |   std |   count |
|:----------------------------------------|-------:|------:|--------:|
| ('bnci2014_001', 'ens_euclid_shind')    | -0.071 | 0.452 |   9.000 |
| ('bnci2014_001', 'ens_euclid_shres')    | -0.274 | 0.209 |   9.000 |
| ('bnci2014_001', 'ens_logeuclid_shind') |  0.048 | 0.416 |   9.000 |
| ('bnci2014_001', 'ens_logeuclid_shres') | -0.015 | 0.270 |   9.000 |
| ('bnci2014_001', 'ens_riemann_shind')   |  0.045 | 0.415 |   9.000 |
| ('bnci2014_001', 'ens_riemann_shres')   | -0.031 | 0.272 |   9.000 |
| ('bnci2014_001', 'euclid')              |  0.134 | 0.282 |   9.000 |
| ('bnci2014_001', 'euclid_shind')        | -0.059 | 0.366 |   9.000 |
| ('bnci2014_001', 'euclid_shres')        |  0.385 | 0.367 |   9.000 |
| ('bnci2014_001', 'feature')             |  0.214 | 0.324 |   9.000 |
| ('bnci2014_001', 'feature_shind')       | -0.034 | 0.470 |   9.000 |
| ('bnci2014_001', 'feature_shres')       |  0.053 | 0.317 |   9.000 |
| ('bnci2014_001', 'logeuclid')           |  0.179 | 0.244 |   9.000 |
| ('bnci2014_001', 'logeuclid_shind')     | -0.053 | 0.470 |   9.000 |
| ('bnci2014_001', 'logeuclid_shres')     |  0.182 | 0.332 |   9.000 |
| ('bnci2014_001', 'riemann')             |  0.181 | 0.227 |   9.000 |
| ('bnci2014_001', 'riemann_shind')       | -0.047 | 0.457 |   9.000 |
| ('bnci2014_001', 'riemann_shres')       |  0.193 | 0.354 |   9.000 |