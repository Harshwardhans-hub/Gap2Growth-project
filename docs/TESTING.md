# Gap2Growth offline tests

The downtime service has pure scheduling logic mixed with database imports. Its unit tests replace the database module at import time, allowing core schedule calculations to be checked without Supabase credentials or network access.

## Run tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

## Covered scenarios

- No timetable data returns no detected gaps.
- A gap between scheduled classes is reported for the requested day.
- Cancelled classes are treated separately from ordinary timetable gaps.
- Combined slots are sorted by start time.
- Daily schedule output places free-time entries between class entries.
- Days with no matching timetable entries produce an empty schedule.\n- Recommendation tests cover preference scoring, duration limits, sorting, category filters, and completed-activity exclusion.\n- Report tests cover global versus student-scoped log retrieval and completed-activity aggregation.

## Extending coverage

When adding a schedule rule, test the smallest qualifying gap, a gap just below the threshold, overlapping or malformed times, a cancelled class, and a day with no classes. Keep database calls mocked so these tests remain deterministic and safe to run in continuous integration.

See [RECOMMENDATION_SCORING.md](RECOMMENDATION_SCORING.md) for the scoring weights, selection pipeline, random tie handling, and personalization fallback policy.
