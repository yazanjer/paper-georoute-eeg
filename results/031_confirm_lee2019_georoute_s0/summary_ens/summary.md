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

## Paired tests vs georoute_ens

| dataset    | ref          | vs                      |   mean_diff |      p |   rank_biserial |   wins |   ties |   losses |   n |   p_holm |
|:-----------|:-------------|:------------------------|------------:|-------:|----------------:|-------:|-------:|---------:|----:|---------:|
| lee2019_mi | georoute_ens | georoute                |      0.0011 | 0.6084 |          0.0958 |     18 |     20 |       16 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute+t3a            |     -0.0402 | 0.0000 |         -0.8699 |      9 |      6 |       39 |  54 |   0.0000 |
| lee2019_mi | georoute_ens | georoute@n10            |      0.0157 | 0.0093 |          0.4253 |     32 |      5 |       17 |  54 |   0.1958 |
| lee2019_mi | georoute_ens | georoute[euclid]        |      0.0013 | 0.5114 |          0.1161 |     23 |     13 |       18 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute[feature]       |     -0.0020 | 0.4948 |         -0.1244 |     21 |     15 |       18 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute[logeuclid]     |      0.0026 | 0.1380 |          0.2703 |     23 |     18 |       13 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute[top1]          |      0.0111 | 0.0024 |          0.5106 |     35 |      8 |       11 |  54 |   0.0587 |
| lee2019_mi | georoute_ens | georoute[top3]          |      0.0015 | 0.5090 |          0.1238 |     21 |     17 |       16 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute[top45]         |      0.0000 | 0.8064 |          0.0439 |     22 |     14 |       18 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute[top5]          |      0.0004 | 0.8196 |          0.0429 |     18 |     19 |       17 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute[top8]          |      0.0004 | 0.7695 |          0.0667 |     13 |     30 |       11 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute_ens@n10        |      0.0170 | 0.0056 |          0.4583 |     30 |      6 |       18 |  54 |   0.1233 |
| lee2019_mi | georoute_ens | georoute_ens[euclid]    |      0.0028 | 0.2174 |          0.2267 |     23 |     16 |       15 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute_ens[feature]   |     -0.0041 | 0.2303 |         -0.2248 |     16 |     17 |       21 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute_ens[logeuclid] |      0.0011 | 0.3354 |          0.2133 |     16 |     30 |        8 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute_ens[top1]      |      0.0111 | 0.0024 |          0.5106 |     35 |      8 |       11 |  54 |   0.0587 |
| lee2019_mi | georoute_ens | georoute_ens[top3]      |     -0.0006 | 0.8261 |         -0.0405 |     20 |     16 |       18 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute_ens[top45]     |      0.0013 | 0.5665 |          0.0999 |     24 |     13 |       17 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute_ens[top5]      |      0.0022 | 0.3173 |          0.2094 |     15 |     26 |       13 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | georoute_ens[top8]      |     -0.0009 | 0.4588 |         -0.1667 |     10 |     30 |       14 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | oracle_best_expert      |     -0.0574 | 0.0000 |         -1.0000 |      0 |      2 |       52 |  54 |   0.0000 |
| lee2019_mi | georoute_ens | oracle_best_single      |     -0.0574 | 0.0000 |         -1.0000 |      0 |      2 |       52 |  54 |   0.0000 |
| lee2019_mi | georoute_ens | random_ens              |      0.0014 | 0.3221 |          0.1608 |     28 |      4 |       22 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | random_route            |      0.0027 | 0.1258 |          0.2486 |     29 |      4 |       21 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | shared_only             |      0.0041 | 0.2451 |          0.2019 |     27 |     11 |       16 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | shared_only+t3a         |     -0.0383 | 0.0000 |         -0.7801 |     11 |      7 |       36 |  54 |   0.0001 |
| lee2019_mi | georoute_ens | uniform_ens             |      0.0015 | 0.4238 |          0.1394 |     24 |     13 |       17 |  54 |   1.0000 |
| lee2019_mi | georoute_ens | uniform_merge           |      0.0004 | 0.8142 |          0.0432 |     22 |     16 |       16 |  54 |   1.0000 |

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