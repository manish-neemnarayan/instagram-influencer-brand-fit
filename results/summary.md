# Experiment summary

Test set: 40 cases, seed 42. Thresholds chosen on a separate 200-case tuning set (seed 11).

`misspecified` = agent guesses the parameters (realistic). `oracle` = agent is handed the true generating parameters (impossible in practice; included to show how much the results depend on being right).

| arm          | policy              |   total_cost |   mean_cost |   signed |   signed_unsafe |   signed_inauthentic |   signed_sophisticated |   declined_clean |   human_review_rate |   probe_rate |
|:-------------|:--------------------|-------------:|------------:|---------:|----------------:|---------------------:|-----------------------:|-----------------:|--------------------:|-------------:|
| misspecified | v0_threshold        |         -119 |      -2.975 |       17 |               0 |                    1 |                      1 |                0 |               0.075 |        0.15  |
| misspecified | v0_expected_cost    |         -137 |      -3.425 |       17 |               0 |                    1 |                      1 |                0 |               0     |        0.075 |
| misspecified | v1_voi              |         -115 |      -2.875 |       16 |               0 |                    1 |                      1 |                0 |               0.075 |        0     |
| misspecified | engagement_baseline |          375 |       9.375 |       28 |               1 |                    7 |                      4 |                4 |               0     |        0     |
| oracle       | v0_threshold        |         -119 |      -2.975 |       17 |               0 |                    1 |                      1 |                0 |               0.075 |        0.15  |
| oracle       | v0_expected_cost    |         -140 |      -3.5   |       17 |               0 |                    1 |                      1 |                0 |               0     |        0     |
| oracle       | v1_voi              |         -140 |      -3.5   |       17 |               0 |                    1 |                      1 |                0 |               0     |        0     |
| oracle       | engagement_baseline |          375 |       9.375 |       28 |               1 |                    7 |                      4 |                4 |               0     |        0     |

## Ground truth in the test set

- inauthentic: 11
- of those, sophisticated: 5
- mismatched: 17
- safety risk: 3
- clean: 16