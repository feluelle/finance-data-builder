with stg_yahoo as (

    select "Ticker"::varchar as ticker,
           "Datetime"::timestamp as datetime,
           "Open"::double precision as "open",
           "High"::double precision as high,
           "Low"::double precision as low,
           "Close"::double precision as "close",
           "Adj Close"::double precision as adj_close,
           "Volume"::numeric::integer as volume,
           "Dividends"::double precision as dividends,
           "Stock Splits"::numeric::integer as stock_splits
    from {{ source('yahoo', 'src_yahoo') }}
    -- filter out null rows
    where not (
      "Open" is null and
      "High" is null and
      "Low" is null and
      "Close" is null and
      "Adj Close" is null and
      "Volume" is null
    )

)
-- TODO: Check if distinct is really necessary
select distinct {{ dbt_utils.surrogate_key(['ticker', 'datetime']) }} as id,
                *
from stg_yahoo