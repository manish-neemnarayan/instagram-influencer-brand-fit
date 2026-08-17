# Calibration

Pooled over 40 runs of 40 cases (1600 cases per arm). Bins on P(clean).

## misspecified (ECE = 0.051)

| bin     |   n |   mean_predicted |   observed_clean |    gap |
|:--------|----:|-----------------:|-----------------:|-------:|
| 0.0-0.2 | 790 |            0.014 |            0.003 |  0.011 |
| 0.2-0.4 |  24 |            0.28  |            0.042 |  0.238 |
| 0.4-0.6 |  15 |            0.5   |            0.2   |  0.3   |
| 0.6-0.8 |  42 |            0.724 |            0.762 | -0.038 |
| 0.8-1.0 | 729 |            0.972 |            0.888 |  0.084 |

## oracle (ECE = 0.053)

| bin     |   n |   mean_predicted |   observed_clean |    gap |
|:--------|----:|-----------------:|-----------------:|-------:|
| 0.0-0.2 | 821 |            0.004 |            0.005 | -0.001 |
| 0.2-0.4 |  11 |            0.276 |            0.364 | -0.088 |
| 0.4-0.6 |   5 |            0.501 |            0.2   |  0.301 |
| 0.6-0.8 |  15 |            0.71  |            0.867 | -0.157 |
| 0.8-1.0 | 748 |            0.992 |            0.886 |  0.105 |

## Pooled metrics

| arm          | policy              |   precision |   recall |   false_positive |   false_negative |   fp_safety_risk |   fp_sophisticated |   human_review_rate |   mean_cost |
|:-------------|:--------------------|------------:|---------:|-----------------:|-----------------:|-----------------:|-------------------:|--------------------:|------------:|
| misspecified | v0_threshold        |       0.886 |    0.964 |               85 |               25 |                5 |                 79 |               0.06  |      -2     |
| misspecified | v0_expected_cost    |       0.894 |    0.924 |               75 |               52 |                0 |                 73 |               0.003 |      -2.922 |
| misspecified | engagement_baseline |       0.466 |    0.778 |              610 |              152 |               56 |                111 |               0     |      10.381 |
| oracle       | v0_threshold        |       0.885 |    0.971 |               86 |               20 |                5 |                 80 |               0.057 |      -2.061 |
| oracle       | v0_expected_cost    |       0.888 |    0.958 |               83 |               29 |                2 |                 78 |               0     |      -2.793 |
| oracle       | engagement_baseline |       0.466 |    0.778 |              610 |              152 |               56 |                111 |               0     |      10.381 |
