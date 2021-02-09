with pre__stg_yahoo_finance as (

    select "VALUE"::jsonb as json_value,
           _ticker
    from {{ source('yahoo', 'src_yahoo_finance') }}

), stg_yahoo_finance as (

    select {{ dbt_utils.surrogate_key(['json_value', '_ticker']) }} as uid,
           "Datetime" as datetime,
           "Open" as "open",
           "High" as high,
           "Low" as low,
           "Close" as "close",
           "Adj Close" as adj_close,
           "Volume" as volume,
           "Dividends" as dividends,
           "Stock Splits" as stock_splits,
           _ticker,
           now() as _loaded_at
    from pre__stg_yahoo_finance, jsonb_to_recordset(json_value) as records(
        "Datetime" timestamp,
        "Open" double precision,
        "High" double precision,
        "Low" double precision,
        "Close" double precision,
        "Adj Close" double precision,
        "Volume" numeric,
        "Dividends" double precision,
        "Stock Splits" numeric
    )

)
-- TODO: Check if distinct is really necessary
select distinct *
from stg_yahoo_finance
-- filter out null rows
where not (
  "open" is null and
  high is null and
  low is null and
  "close" is null and
  adj_close is null and
  volume is null
)