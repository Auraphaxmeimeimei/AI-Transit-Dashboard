## Codebook

| Column | Type | Description |
|---|---|---|
| ts | string | Timestamp in ISO format, one per generated frame |
| cars | integer | Simulated vehicle count, random range (5–30) |
| buses | integer | Simulated bus count, random range (0–3) |
| trucks | integer | Simulated truck count, random range (0–5) |

Notes:
1. metrics.csv is generated automatically when AI Detection is triggered.
2. Output supports visualization, ETA estimation, delay calculation and advisory models.
