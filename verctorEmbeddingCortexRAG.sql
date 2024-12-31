-- Define the question
SET question = 'I am a Project Management. I need to create system inventory management. What kind of skill I need to my developer?';

-- Step 1: Retrieve relevant context using Cortex Search
WITH context AS (
    SELECT 
        name,
        chunk_text,
        snowflake.cortex.search(
            'snowflake-arctic-search-v1', -- Cortex Search model or index name
            chunk_text, 
            $question, 
            mode => 'hybrid',             -- Use 'hybrid' mode for combining full-text and vector search
            filters => '{ "type": "skill" }' -- (Optional) Filter by metadata (e.g., type = 'skill')
        ) AS search_score
    FROM 
        "HELP_PM"."PUBLIC"."CONTENT_CHUNKS"
    WHERE 
        search_score > 0.5 -- Threshold for relevance
    ORDER BY 
        search_score DESC
    LIMIT 10
),

-- Step 2: Concatenate retrieved chunks into a single context
concatenated_context AS (
    SELECT 
        LISTAGG(chunk_text, ' ') WITHIN GROUP (ORDER BY name) AS combined_context
    FROM 
        context
)

-- Step 3: Generate LLM response
SELECT 
    snowflake.cortex.complete(
        'mistral-large2', 
        'Here is our analysis of our employee, please just select the related employee who can help to our question. Make sure your narrative explains the project and the reason. ' ||
        '###
        CONTEXT: ' || combined_context || '
        ###
        QUESTION: ' || $question || '
        ANSWER: '
    ) AS response
FROM 
    concatenated_context;
