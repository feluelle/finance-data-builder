with pre__stg_google_news as (

    select "VALUE"::jsonb as json_value
    from {{ source('google', 'src_google_news') }}

), stg_google_news as (

    select {{ dbt_utils.surrogate_key(['json_value']) }} as uid,
           json_value -> 'feed' as feed,
           json_value -> 'entries' as entries,
           now() as _loaded_at
    from pre__stg_google_news

)

select *
from stg_google_news