with stg_paypal_transactions__details_info as (

    select uid,
           transaction_info ->> 'paypal_account_id' as paypal_account_id,
           transaction_info ->> 'transaction_id' as transaction_id,
           transaction_info ->> 'paypal_reference_id' as paypal_reference_id,
           transaction_info ->> 'paypal_reference_id_type' as paypal_reference_id_type,
           transaction_info ->> 'transaction_event_code' as transaction_event_code,
           (transaction_info ->> 'transaction_initiation_date')::date as transaction_initiation_date,
           (transaction_info ->> 'transaction_updated_date')::date as transaction_updated_date,
           transaction_info -> 'transaction_amount' as transaction_amount,
           transaction_info ->> 'transaction_status' as transaction_status,
           transaction_info -> 'ending_balance' as ending_balance,
           transaction_info -> 'available_balance' as available_balance,
           transaction_info ->> 'invoice_id' as invoice_id,
           transaction_info ->> 'protection_eligibility' as protection_eligibility,
           now() as _loaded_at
    from {{ ref('stg_paypal_transactions__details') }}

)

select *
from stg_paypal_transactions__details_info