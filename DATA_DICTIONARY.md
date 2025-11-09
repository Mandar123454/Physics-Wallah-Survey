# Data Dictionary: Physics Wallah Student Experience Survey

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| respondent_id | integer | Synthetic unique identifier (original respondent IDs removed for privacy) | 1,2,3 |
| satisfaction_score | integer (1-10) | Overall satisfaction with Physics Wallah platform | 8 |
| recommend_score | integer (0-10) | Likelihood to recommend (used for NPS grouping: 0-6 Detractor, 7-8 Passive, 9-10 Promoter) | 9 |
| content_quality | categorical | Perceived learning content quality | High, Medium, Low |
| platform_usability | categorical | Usability & navigation experience | Excellent, Good, Average, Poor |
| value_for_money | categorical | Perceived subscription/price value | High, Medium, Low |
| usage_frequency | categorical | Typical usage frequency | Daily, Weekly, Monthly |
| device | categorical | Primary device used | Mobile, Desktop, Tablet |
| open_feedback | free text | Anonymous qualitative feedback comment | "Great content, helped me a lot" |

## Notes
- Personally identifiable info (names, emails) has been removed.
- This sample is a reduced illustrative subset (5 rows). Replace with full cleaned dataset when ready.
- Ensure consistent controlled vocabulary for categorical fields to avoid analysis drift.
