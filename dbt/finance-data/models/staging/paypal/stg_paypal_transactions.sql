with pre__stg_paypal_transactions as (

    select "VALUE"::jsonb as json_value
    from {{ source('paypal', 'src_paypal_transactions') }}

), stg_paypal_transactions as (

    select {{ dbt_utils.surrogate_key(['json_value']) }} as uid,
           json_value -> 'transaction_details' as transaction_details,
           json_value ->> 'account_number' as account_number,
           (json_value ->> 'start_date')::date as start_date,
           (json_value ->> 'end_date')::date as end_date,
           (json_value ->> 'last_refreshed_datetime')::date as last_refreshed_datetime,
           (json_value ->> 'page')::int as page,
           (json_value ->> 'total_items')::int as total_items,
           (json_value ->> 'total_pages')::int as total_pages,
           json_value -> 'links' as links,
           now() as _loaded_at
    from pre__stg_paypal_transactions

)

select *
from stg_paypal_transactions