# Feature Engineering — CreatorFlow

## Purpose
Derives 5 families of features from a cleaned DataFrame.

## Feature Families

### 1. Engagement
| Column | Formula |
|---|---|
| `total_interactions` | likes + comments + shares |
| `engagement_rate` | total_interactions / impressions (0 if impressions = 0) |

### 2. Temporal
| Column | Source |
|---|---|
| `post_hour` | hour of day (0–23) |
| `post_day_of_week` | 0 = Monday, 6 = Sunday |
| `is_weekend` | 1 if Sat/Sun |
| `post_month` | 1–12 |
| `post_week_of_year` | ISO week 1–53 |

### 3. Content
| Column | Description |
|---|---|
| `caption_length` | Character count |
| `word_count` | Whitespace-separated tokens |
| `hashtag_count` | `#word` occurrences |
| `mention_count` | `@word` occurrences |
| `url_count` | `http(s)://...` occurrences |
| `emoji_count` | Unicode emoji ranges |

### 4. Historical
| Column | Description |
|---|---|
| `rolling_avg_engagement` | Mean engagement rate of previous 5 posts |
| `days_since_last_post` | Days between consecutive posts |
| `posting_frequency_7d` | Posts in trailing 7-day window |

### 5. Sentiment
| Column | Description |
|---|---|
| `sentiment_score` | VADER compound score (−1 to +1) on caption |

## Output
`(featured_df, FeatureReport)`. The report contains the list of derived columns,
per-action messages, and a 5-row sample for preview.

## Notes
- VADER is optional; if not installed, sentiment defaults to 0.0.
- Historical features require the DataFrame to be sorted by date — this is done
  internally.