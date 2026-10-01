-- 4.7.6
-- Store grounded structured AI extraction for each CV.
--
-- JSONB is used because CVAIExtraction is already represented
-- as structured JSON by the application layer.

ALTER TABLE cvs
ADD COLUMN IF NOT EXISTS ai_extraction JSONB;
