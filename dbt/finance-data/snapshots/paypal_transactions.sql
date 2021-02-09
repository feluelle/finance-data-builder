{% snapshot paypal_transactions_snapshot %}

{{
    config(
      unique_key="uid",
    )
}}

select {{ dbt_utils.surrogate_key(['"VALUE"']) }} as uid,
       *
from {{ source('paypal', 'src_paypal_transactions') }}

{% endsnapshot %}