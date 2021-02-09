with stg_paypal_transactions__details as (

    select uid,
           transaction_detail -> 'transaction_info' as transaction_info,
           now() as _loaded_at
    from {{ ref('stg_paypal_transactions') }}, jsonb_array_elements(transaction_details) as transaction_detail

)

select *
from stg_paypal_transactions__details