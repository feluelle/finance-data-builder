{% snapshot paypal_transactions_snapshot %}

{{
    config(
      unique_key="_dbt_id",
    )
}}

select {{ dbt_utils.surrogate_key(['transaction_details']) }} as _dbt_id,
       *
from {{ source('paypal', 'src_paypal_transactions') }}

{% endsnapshot %}