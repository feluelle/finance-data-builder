{% snapshot google_news_snapshot %}

{{
    config(
      unique_key="_dbt_id",
    )
}}

select {{ dbt_utils.surrogate_key(['title', 'link', 'published', '"Company"']) }} as _dbt_id,
       *
from {{ source('google_news', 'src_google_news') }}

{% endsnapshot %}