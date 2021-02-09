{% snapshot google_news_snapshot %}

{{
    config(
      unique_key="uid",
    )
}}

select {{ dbt_utils.surrogate_key(['"VALUE"']) }} as uid,
       *
from {{ source('google', 'src_google_news') }}

{% endsnapshot %}