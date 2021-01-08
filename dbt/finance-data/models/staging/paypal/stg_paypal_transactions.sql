with pre__stg_paypal_transactions as (

    select replace(transaction_details, '''', '"')::jsonb as transaction_details,
           account_number,
           start_date::date as start_date,
           end_date::date as end_date,
           last_refreshed_datetime::date as last_refreshed_datetime
    from {{ source('paypal', 'src_paypal_transactions') }}

), stg_paypal_transactions as (

    select account_number,
           start_date,
           end_date,
           last_refreshed_datetime,
           transaction_details -> 'transaction_info' ->> 'paypal_account_id' as paypal_account_id,
           transaction_details -> 'transaction_info' ->> 'transaction_id' as transaction_id,
           transaction_details -> 'transaction_info' ->> 'paypal_reference_id' as paypal_reference_id,
           transaction_details -> 'transaction_info' ->> 'paypal_reference_id_type' as paypal_reference_id_type,
           (transaction_details -> 'transaction_info' ->> 'transaction_initiation_date')::date as transaction_initiation_date,
           (transaction_details -> 'transaction_info' ->> 'transaction_updated_date')::date as transaction_updated_date,
           transaction_details -> 'transaction_info' -> 'transaction_amount' ->> 'currency_code' as transaction_amount__currency_code,
           (transaction_details -> 'transaction_info' -> 'transaction_amount' ->> 'value')::double precision as transaction_amount__value,
           transaction_details -> 'transaction_info' ->> 'transaction_status' as transaction_status,
           transaction_details -> 'transaction_info' -> 'ending_balance' ->> 'currency_code' as ending_balance__currency_code,
           (transaction_details -> 'transaction_info' -> 'ending_balance' ->> 'value')::double precision as ending_balance__value,
           transaction_details -> 'transaction_info' -> 'available_balance' ->> 'currency_code' as available_balance__currency_code,
           (transaction_details -> 'transaction_info' -> 'available_balance' ->> 'value')::double precision as available_balance__value,
           transaction_details -> 'transaction_info' ->> 'invoice_id' as invoice_id,
           transaction_details -> 'transaction_info' ->> 'protection_eligibility' as protection_eligibility
    from pre__stg_paypal_transactions

)

select {{ dbt_utils.surrogate_key(['transaction_id']) }} as id,
       *
from stg_paypal_transactions