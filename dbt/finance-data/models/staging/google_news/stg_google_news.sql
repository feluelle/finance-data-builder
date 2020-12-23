with stg_google_news as (

    select title,
           link,
           "published"::date as published_at,
           "Company" as company
    from {{ source('google_news', 'src_google_news') }}

)
-- TODO: Check if distinct is really necessary
select distinct {{ dbt_utils.surrogate_key(['title', 'link', 'published_at', 'company']) }} as id,
                *
from stg_google_news