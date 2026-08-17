# Replication summary

30 independent runs of 40 cases each, seeds 1000-1029. Agent uses misspecified parameters throughout (the realistic arm).

## Mean per run

| policy              |   total_cost |   signed_unsafe |   signed_sophisticated |   declined_clean |   human_review_rate |   gift_rate |   analytics_rate |
|:--------------------|-------------:|----------------:|-----------------------:|-----------------:|--------------------:|------------:|-----------------:|
| engagement_baseline |      426.667 |           1.5   |                  3.5   |            3.133 |               0     |           0 |            0     |
| v0_expected_cost    |     -117.533 |           0     |                  1.933 |            0     |               0.003 |           0 |            0.082 |
| v0_threshold        |     -100.1   |           0.033 |                  2     |            0.133 |               0.059 |           0 |            0.152 |
| v1_voi              |      -99.767 |           0     |                  1.733 |            0.033 |               0.076 |           0 |            0.01  |

## Cost spread

| policy              |   count |   mean |   std |   min |    25% |   50% |   75% |   max |
|:--------------------|--------:|-------:|------:|------:|-------:|------:|------:|------:|
| engagement_baseline |      30 |  426.7 | 250.4 |    55 |  237.5 |   380 | 656.2 |  1015 |
| v0_expected_cost    |      30 | -117.5 |  39.3 |  -196 | -145.5 |  -127 | -93.8 |   -38 |
| v0_threshold        |      30 | -100.1 |  41   |  -168 | -126.2 |  -107 | -84.5 |    18 |
| v1_voi              |      30 |  -99.8 |  41.3 |  -180 | -124.8 |  -104 | -81.2 |     5 |

## Failure conditions (pooled across all runs)

| policy              | failure                   |   n |
|:--------------------|:--------------------------|----:|
| engagement_baseline | declined_clean            |  94 |
| engagement_baseline | signed_crude_fake         |  58 |
| engagement_baseline | signed_mismatch           | 262 |
| engagement_baseline | signed_safety_risk        |  45 |
| engagement_baseline | signed_sophisticated_fake |  98 |
| v0_expected_cost    | signed_mismatch           |   2 |
| v0_expected_cost    | signed_sophisticated_fake |  58 |
| v0_threshold        | declined_clean            |   4 |
| v0_threshold        | signed_mismatch           |   2 |
| v0_threshold        | signed_safety_risk        |   1 |
| v0_threshold        | signed_sophisticated_fake |  60 |
| v1_voi              | declined_clean            |   1 |
| v1_voi              | signed_mismatch           |   2 |
| v1_voi              | signed_sophisticated_fake |  52 |