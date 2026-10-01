-- 4.8.6
-- Store grounded structured AI analysis for each CV.
--
-- JSONB is used because CVAnalysis is represented
-- as structured JSON by the application layer.

ALTER TABLE cvs
ADD COLUMN IF NOT EXISTS ai_analysis JSONB;
