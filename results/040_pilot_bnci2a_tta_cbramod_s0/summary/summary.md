# Summary

| dataset      | method                   |   acc_mean |   acc_sd_subjects |   acc_sd_seeds |   kappa_mean |   n_subjects |   n_seeds |
|:-------------|:-------------------------|-----------:|------------------:|---------------:|-------------:|-------------:|----------:|
| bnci2014_001 | rctta+t3a_cbramod        |     0.6397 |            0.1555 |            nan |       0.5195 |            9 |         1 |
| bnci2014_001 | t3a_cbramod              |     0.6354 |            0.1498 |            nan |       0.5139 |            9 |         1 |
| bnci2014_001 | rctta_lam2_cbramod       |     0.6154 |            0.1616 |            nan |       0.4871 |            9 |         1 |
| bnci2014_001 | rctta_cbramod            |     0.6069 |            0.1445 |            nan |       0.4758 |            9 |         1 |
| bnci2014_001 | rctta_offline_cbramod    |     0.6065 |            0.1435 |            nan |       0.4753 |            9 |         1 |
| bnci2014_001 | rctta_norecenter_cbramod |     0.6061 |            0.1453 |            nan |       0.4748 |            9 |         1 |
| bnci2014_001 | rctta_nogate_cbramod     |     0.6057 |            0.1465 |            nan |       0.4743 |            9 |         1 |
| bnci2014_001 | rctta_lam0.5_cbramod     |     0.5999 |            0.1377 |            nan |       0.4666 |            9 |         1 |
| bnci2014_001 | source_cbramod           |     0.5976 |            0.1332 |            nan |       0.4635 |            9 |         1 |
| bnci2014_001 | rctta_nobp_cbramod       |     0.5945 |            0.1418 |            nan |       0.4594 |            9 |         1 |
| bnci2014_001 | lame_cbramod             |     0.5436 |            0.1561 |            nan |       0.3915 |            9 |         1 |
| bnci2014_001 | shot_im_cbramod          |     0.4954 |            0.1504 |            nan |       0.3272 |            9 |         1 |
| bnci2014_001 | geo_src_cbramod          |     0.4676 |            0.1399 |            nan |       0.2901 |            9 |         1 |
| bnci2014_001 | tent_cbramod             |     0.4633 |            0.1259 |            nan |       0.2845 |            9 |         1 |

## Paired tests vs rctta_cbramod

| dataset      | ref           | vs                       |   mean_diff |      p |   rank_biserial |   wins |   ties |   losses |   n |   p_holm |
|:-------------|:--------------|:-------------------------|------------:|-------:|----------------:|-------:|-------:|---------:|----:|---------:|
| bnci2014_001 | rctta_cbramod | geo_src_cbramod          |      0.1393 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.0508 |
| bnci2014_001 | rctta_cbramod | lame_cbramod             |      0.0633 | 0.0273 |          0.8222 |      8 |      0 |        1 |   9 |   0.2188 |
| bnci2014_001 | rctta_cbramod | rctta+t3a_cbramod        |     -0.0328 | 0.0078 |         -0.9556 |      1 |      0 |        8 |   9 |   0.0859 |
| bnci2014_001 | rctta_cbramod | rctta_lam0.5_cbramod     |      0.0069 | 0.1562 |          0.5833 |      6 |      1 |        2 |   9 |   0.9375 |
| bnci2014_001 | rctta_cbramod | rctta_lam2_cbramod       |     -0.0085 | 0.5312 |         -0.2778 |      4 |      1 |        4 |   9 |   1.0000 |
| bnci2014_001 | rctta_cbramod | rctta_nobp_cbramod       |      0.0123 | 0.0312 |          0.8889 |      7 |      1 |        1 |   9 |   0.2188 |
| bnci2014_001 | rctta_cbramod | rctta_nogate_cbramod     |      0.0012 | 0.5000 |          0.6000 |      3 |      5 |        1 |   9 |   1.0000 |
| bnci2014_001 | rctta_cbramod | rctta_norecenter_cbramod |      0.0008 | 0.5000 |          1.0000 |      2 |      7 |        0 |   9 |   1.0000 |
| bnci2014_001 | rctta_cbramod | rctta_offline_cbramod    |      0.0004 | 0.8750 |          0.2000 |      3 |      5 |        1 |   9 |   1.0000 |
| bnci2014_001 | rctta_cbramod | shot_im_cbramod          |      0.1115 | 0.0039 |          1.0000 |      9 |      0 |        0 |   9 |   0.0508 |
| bnci2014_001 | rctta_cbramod | source_cbramod           |      0.0093 | 0.1797 |          0.5556 |      5 |      1 |        3 |   9 |   0.9375 |
| bnci2014_001 | rctta_cbramod | t3a_cbramod              |     -0.0285 | 0.0078 |         -0.9556 |      1 |      0 |        8 |   9 |   0.0859 |
| bnci2014_001 | rctta_cbramod | tent_cbramod             |      0.1435 | 0.0078 |          0.9556 |      8 |      0 |        1 |   9 |   0.0859 |

