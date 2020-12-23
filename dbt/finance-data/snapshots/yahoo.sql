{% snapshot yahoo_snapshot %}

{{
    config(
      unique_key="_dbt_id",
    )
}}

select {{ dbt_utils.surrogate_key(['"Ticker"', '"Datetime"']) }} as _dbt_id,
       *
from {{ source('yahoo', 'src_yahoo') }}

{% endsnapshot %}