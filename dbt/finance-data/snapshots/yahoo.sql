{% snapshot yahoo_snapshot %}

{{
    config(
      unique_key="ticker || '-' || datetime",
    )
}}

select * from {{ source('yahoo', 'src_yahoo') }}

{% endsnapshot %}