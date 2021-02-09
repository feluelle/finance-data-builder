with stg_google_news__feed as (

    select uid,
           feed -> 'generator_detail' as generator_detail,
           feed ->> 'generator' as generator,
           feed ->> 'title' as title,
           feed -> 'title_detail' as title_detail,
           feed -> 'links' as links,
           feed ->> 'link' as link,
           feed ->> 'language' as "language",
           feed ->> 'publisher' as publisher,
           feed -> 'publisher_detail' as publisher_detail,
           feed ->> 'rights' as rights,
           feed -> 'rights_detail' as rights_detail,
           feed ->> 'updated' as updated,
           feed -> 'updated_parsed' as updated_parsed,
           feed ->> 'subtitle' as subtitle,
           feed -> 'subtitle_detail' as subtitle_detail,
           now() as _loaded_at
    from {{ ref('stg_google_news') }}

)

select *
from stg_google_news__feed