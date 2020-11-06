with stg_yahoo as (

    select "Ticker"::varchar as ticker,
           "Datetime"::timestamp as datetime,
           "Open"::double precision as "open",
           "High"::double precision as high,
           "Low"::double precision as low,
           "Close"::double precision as "close",
           "Adj Close"::double precision as adj_close,
           "Volume"::int as volume,
           "Dividends"::double precision as dividends,
           "Stock Splits"::int as stock_splits
    from {{ source('yahoo', 'src_yahoo') }}

)

select *
from stg_yahoo