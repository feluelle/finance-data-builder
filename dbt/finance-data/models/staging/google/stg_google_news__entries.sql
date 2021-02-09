with stg_google_news__entries as (

    select uid,
           entry ->> 'title' as title,
           entry -> 'title_detail' as title_detail,
           entry -> 'links' as links,
           entry ->> 'link' as link,
           entry ->> 'id' as id,
           entry ->> 'guidislink' as guidislink,
           entry ->> 'published' as published,
           entry -> 'published_parsed' as published_parsed,
           entry ->> 'summary' as summary,
           entry -> 'summary_detail' as summary_detail,
           entry -> 'source' as "source",
           entry -> 'sub_articles' as sub_articles,
           now() as _loaded_at
    from {{ ref('stg_google_news') }}, jsonb_array_elements(entries) as entry

)

select *
from stg_google_news__entries