# Summary

| dataset    | method                  |   acc_mean |   acc_sd_subjects |   acc_sd_seeds |   kappa_mean |   n_subjects |   n_seeds |
|:-----------|:------------------------|-----------:|------------------:|---------------:|-------------:|-------------:|----------:|
| lee2019_mi | oracle_best_expert      |     0.8137 |            0.1037 |            nan |     nan      |           54 |         1 |
| lee2019_mi | oracle_best_single      |     0.8137 |            0.1037 |            nan |     nan      |           54 |         1 |
| lee2019_mi | georoute+t3a            |     0.7965 |            0.1118 |            nan |       0.5930 |           54 |         1 |
| lee2019_mi | shared_only+t3a         |     0.7946 |            0.1097 |            nan |       0.5893 |           54 |         1 |
| lee2019_mi | georoute_ens[feature]   |     0.7604 |            0.1151 |            nan |       0.5207 |           54 |         1 |
| lee2019_mi | georoute[feature]       |     0.7583 |            0.1160 |            nan |       0.5167 |           54 |         1 |
| lee2019_mi | georoute_ens[top8]      |     0.7572 |            0.1127 |            nan |       0.5144 |           54 |         1 |
| lee2019_mi | georoute_ens[top3]      |     0.7569 |            0.1146 |            nan |       0.5137 |           54 |         1 |
| lee2019_mi | georoute[top45]         |     0.7563 |            0.1135 |            nan |       0.5126 |           54 |         1 |
| lee2019_mi | georoute_ens            |     0.7563 |            0.1143 |            nan |       0.5126 |           54 |         1 |
| lee2019_mi | uniform_merge           |     0.7559 |            0.1140 |            nan |       0.5119 |           54 |         1 |
| lee2019_mi | georoute[top5]          |     0.7559 |            0.1133 |            nan |       0.5119 |           54 |         1 |
| lee2019_mi | georoute[top8]          |     0.7559 |            0.1120 |            nan |       0.5119 |           54 |         1 |
| lee2019_mi | georoute                |     0.7552 |            0.1136 |            nan |       0.5104 |           54 |         1 |
| lee2019_mi | georoute_ens[logeuclid] |     0.7552 |            0.1158 |            nan |       0.5104 |           54 |         1 |
| lee2019_mi | georoute[euclid]        |     0.7550 |            0.1116 |            nan |       0.5100 |           54 |         1 |
| lee2019_mi | georoute_ens[top45]     |     0.7550 |            0.1135 |            nan |       0.5100 |           54 |         1 |
| lee2019_mi | random_ens              |     0.7549 |            0.1138 |            nan |     nan      |           54 |         1 |
| lee2019_mi | georoute[top3]          |     0.7548 |            0.1160 |            nan |       0.5096 |           54 |         1 |
| lee2019_mi | uniform_ens             |     0.7548 |            0.1133 |            nan |       0.5096 |           54 |         1 |
| lee2019_mi | georoute_ens[top5]      |     0.7541 |            0.1131 |            nan |       0.5081 |           54 |         1 |
| lee2019_mi | georoute[logeuclid]     |     0.7537 |            0.1138 |            nan |       0.5074 |           54 |         1 |
| lee2019_mi | random_route            |     0.7536 |            0.1123 |            nan |     nan      |           54 |         1 |
| lee2019_mi | georoute_ens[euclid]    |     0.7535 |            0.1135 |            nan |       0.5070 |           54 |         1 |
| lee2019_mi | shared_only             |     0.7522 |            0.1131 |            nan |       0.5044 |           54 |         1 |
| lee2019_mi | georoute[top1]          |     0.7452 |            0.1147 |            nan |       0.4904 |           54 |         1 |
| lee2019_mi | georoute_ens[top1]      |     0.7452 |            0.1147 |            nan |       0.4904 |           54 |         1 |
| lee2019_mi | georoute@n10            |     0.7406 |            0.1211 |            nan |       0.4811 |           54 |         1 |
| lee2019_mi | georoute_ens@n10        |     0.7393 |            0.1228 |            nan |       0.4785 |           54 |         1 |

## Paired tests vs georoute

| dataset    | ref      | vs                      |   mean_diff |      p |   rank_biserial |   wins |   ties |   losses |   n |   p_holm |
|:-----------|:---------|:------------------------|------------:|-------:|----------------:|-------:|-------:|---------:|----:|---------:|
| lee2019_mi | georoute | georoute+t3a            |     -0.0413 | 0.0000 |         -0.8879 |      6 |     10 |       38 |  54 |   0.0000 |
| lee2019_mi | georoute | georoute@n10            |      0.0146 | 0.0308 |          0.3608 |     29 |      7 |       18 |  54 |   0.6470 |
| lee2019_mi | georoute | georoute[euclid]        |      0.0002 | 0.9242 |          0.0171 |     22 |     14 |       18 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute[feature]       |     -0.0031 | 0.2547 |         -0.2162 |     14 |     18 |       22 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute[logeuclid]     |      0.0015 | 0.1834 |          0.3143 |     12 |     34 |        8 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute[top1]          |      0.0100 | 0.0098 |          0.4348 |     33 |      8 |       13 |  54 |   0.2352 |
| lee2019_mi | georoute | georoute[top3]          |      0.0004 | 0.8027 |          0.0441 |     21 |     13 |       20 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute[top45]         |     -0.0011 | 0.8551 |         -0.0341 |     20 |     17 |       17 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute[top5]          |     -0.0007 | 0.7529 |         -0.0665 |     13 |     26 |       15 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute[top8]          |     -0.0007 | 0.6316 |         -0.1087 |     10 |     31 |       13 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute_ens            |     -0.0011 | 0.6084 |         -0.0958 |     16 |     20 |       18 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute_ens@n10        |      0.0159 | 0.0168 |          0.3954 |     29 |      6 |       19 |  54 |   0.3693 |
| lee2019_mi | georoute | georoute_ens[euclid]    |      0.0017 | 0.3901 |          0.1495 |     22 |     12 |       20 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute_ens[feature]   |     -0.0052 | 0.0918 |         -0.3024 |     15 |     14 |       25 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute_ens[logeuclid] |      0.0000 | 0.7828 |          0.0535 |     18 |     21 |       15 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute_ens[top1]      |      0.0100 | 0.0098 |          0.4348 |     33 |      8 |       13 |  54 |   0.2352 |
| lee2019_mi | georoute | georoute_ens[top3]      |     -0.0017 | 0.5579 |         -0.1080 |     18 |     16 |       20 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute_ens[top45]     |      0.0002 | 0.9343 |          0.0159 |     19 |     19 |       16 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute_ens[top5]      |      0.0011 | 0.7108 |          0.0698 |     17 |     19 |       18 |  54 |   1.0000 |
| lee2019_mi | georoute | georoute_ens[top8]      |     -0.0020 | 0.2183 |         -0.2370 |     15 |     20 |       19 |  54 |   1.0000 |
| lee2019_mi | georoute | oracle_best_expert      |     -0.0585 | 0.0000 |         -0.9958 |      1 |      1 |       52 |  54 |   0.0000 |
| lee2019_mi | georoute | oracle_best_single      |     -0.0585 | 0.0000 |         -0.9958 |      1 |      1 |       52 |  54 |   0.0000 |
| lee2019_mi | georoute | random_ens              |      0.0003 | 0.8658 |          0.0275 |     25 |      4 |       25 |  54 |   1.0000 |
| lee2019_mi | georoute | random_route            |      0.0016 | 0.6156 |          0.0816 |     26 |      4 |       24 |  54 |   1.0000 |
| lee2019_mi | georoute | shared_only             |      0.0030 | 0.6289 |          0.0853 |     25 |     12 |       17 |  54 |   1.0000 |
| lee2019_mi | georoute | shared_only+t3a         |     -0.0394 | 0.0000 |         -0.7993 |      9 |      8 |       37 |  54 |   0.0001 |
| lee2019_mi | georoute | uniform_ens             |      0.0004 | 0.8613 |          0.0327 |     21 |     17 |       16 |  54 |   1.0000 |
| lee2019_mi | georoute | uniform_merge           |     -0.0007 | 0.8995 |         -0.0240 |     20 |     18 |       16 |  54 |   1.0000 |

## Distance -> transfer Spearman (mean over subjects/seeds)

|                                 |   mean |   std |   count |
|:--------------------------------|-------:|------:|--------:|
| ('lee2019_mi', 'ens_euclid')    | -0.022 | 0.141 |  53.000 |
| ('lee2019_mi', 'ens_logeuclid') | -0.011 | 0.162 |  53.000 |
| ('lee2019_mi', 'ens_riemann')   | -0.006 | 0.159 |  53.000 |
| ('lee2019_mi', 'euclid')        | -0.022 | 0.141 |  53.000 |
| ('lee2019_mi', 'feature')       |  0.059 | 0.174 |  53.000 |
| ('lee2019_mi', 'logeuclid')     | -0.011 | 0.162 |  53.000 |
| ('lee2019_mi', 'riemann')       | -0.006 | 0.159 |  53.000 |