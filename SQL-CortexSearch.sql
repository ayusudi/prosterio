SHOW CORTEX SEARCH SERVICES

GRANT USAGE ON DATABASE help_pm TO ROLE accountadmin;
GRANT USAGE ON SCHEMA public TO ROLE accountadmin;
GRANT USAGE ON CORTEX SEARCH SERVICE search_employee TO ROLE accountadmin;

SELECT PARSE_JSON(
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
      'help_pm.public.search_employee',
      '{
        "query": "I am creating inventory system, what kind of skill that my developer need and who is the recommendation",
        "columns":[
            "chunk_text",
            "pm_email"
        ],
        "filter": {"@eq": {"pm_email": "ayusudi.abc@gmail.com"} }
      }'
  )
)['results'] as results;
