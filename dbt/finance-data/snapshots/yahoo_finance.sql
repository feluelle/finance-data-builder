{% snapshot yahoo_finance_snapshot %}

{{
    config(
      unique_key="uid",
    )
}}

select {{ dbt_utils.surrogate_key(['"VALUE"', '_ticker']) }} as uid,
       *
from {{ source('yahoo', 'src_yahoo_finance') }}

{% endsnapshot %}