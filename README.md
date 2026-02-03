# TravelSurveyDB (Accessible Travel Survey Taxonomy DB)

This repo contains the backend data model and ingestion pipeline I built for an **Accessible Travel Survey**.

Hotels complete an Alchemer survey describing how well they accommodate different accessibility needs (e.g., mobility, vision, dwarfism). Survey responses are ingested automatically into a PostgreSQL database.

## What’s in here

- **PostgreSQL schema** for hotels, survey responses, questions, disabilities, and taxonomy mappings
- **Alembic migrations** for schema evolution (`alembic/versions/`)
- **Survey ingestion** from Alchemer into the DB (AWS Lambda + SQS style)
- **Taxonomy migration** tooling to sync a spreadsheet-defined taxonomy into the DB

## High-level architecture

1. **Alchemer webhook** hits an AWS Lambda handler (`api/survey_receiver.survey_receiver`).
2. The handler authenticates the request, validates it’s the correct survey + completed status, then creates a `survey_responses` row.
3. It sends an SQS message (`{"id": <db_survey_response_id>, "action": "process_survey"}`) to kick off async processing.
4. A second Lambda handler (`api/survey_ingestions.entry.ingest_survey`) consumes the message and calls the ingestor.
5. The ingestor (`api/survey_ingestions.ingestor.SurveyIngestor`) fetches the full response from Alchemer, locates the hotel (Google Place ID), and writes `answers` rows linked to the canonical `questions` table.

## Data model (summary)

Core entities:

- `hotels`, `hotel_chains`, `contacts`
- `survey_responses` (a record that a response was received/ingested)
- `questions` + `scoring_rules` (rules and thresholds are stored alongside questions)
- `answers` (raw response stored; `normalized_score` is available for downstream scoring/analysis)

Taxonomy entities:

- `disabilities` (+ `market_data`)
- `medical_categories`, `travel_categories`
- mapping tables like `question_disability_map` and `question_travel_category_map`

## Taxonomy migration

`taxonomy_migration/` contains a migrator that reads a taxonomy spreadsheet (questions + taxonomy grids) and syncs it into the DB:

- adds new questions/categories/disabilities
- updates changed definitions/notes/scoring rule fields and mapping “reason” text
- deletes entities/mappings that no longer exist in the spreadsheet

This is intended to keep the DB taxonomy aligned with a spreadsheet maintained by non-developers.

## Scoring approach

Each question can be associated with a scoring rule (operator + thresholds + max score). Scores are computed by awarding points per answered question and normalizing within a category:

`score = sum(points_awarded) / sum(max_possible_for_answered_questions)`

In addition to the score, the system can track **coverage** (how many expected questions were actually answered), so downstream consumers can distinguish “good score with low data” from “good score with high confidence”.

## Tech stack

- Python
- SQLModel / SQLAlchemy
- Alembic migrations
- PostgreSQL (intended for AWS RDS)
- AWS Lambda + SQS pattern
- Alchemer API + webhook
- Google Maps Places API (hotel validation via Place ID)
