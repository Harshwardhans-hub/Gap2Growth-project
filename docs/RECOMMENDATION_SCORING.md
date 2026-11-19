# Activity recommendation scoring

Gap2Growth currently uses a transparent rule-based relevance score; it does not train a machine-learning ranking model.

## Score components

| Signal | Points |
|---|---:|
| Exact course match | 30 |
| Missing course metadata | 15 |
| Category match | 20 |
| Difficulty match | 15 |
| Delivery-mode match | 15 |
| Duration fit | 0–20 |

The duration component is calculated as the integer part of:

`activity_duration_minutes / available_minutes × 20`

and capped at 20 points. The score is additive, so the maximum with all preference matches is 100.

## Selection behavior

1. Activities longer than the available time are removed.
2. Each remaining activity receives its relevance score.
3. Results are sorted from highest to lowest score.
4. Items with equal scores may appear in randomized order.
5. Personalized recommendations infer a preferred category from completed activity history and exclude the last ten completed activity IDs when possible. If that exclusion would leave no results, the service falls back to the full recommendation list.

## Interpretation

This score is a heuristic for sorting suggestions, not a measure of student ability, learning quality, or guaranteed usefulness. Missing metadata can change ranking. The current logic should be evaluated with real student feedback before being used for high-impact decisions.
