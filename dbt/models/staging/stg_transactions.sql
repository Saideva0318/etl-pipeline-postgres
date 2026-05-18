-- =============================================================================
-- dbt Staging Model: stg_transactions
-- Cleans and standardises raw transaction data from the source schema.
-- Run: dbt run --select stg_transactions
-- Test: dbt test --select stg_transactions
-- =============================================================================

{{ config(
    materialized = 'view',
    schema       = 'staging'
) }}

with source as (

    select * from {{ source('raw', 'transactions') }}

),

cleaned as (

    select
        -- Primary key
        transaction_id::bigint                              as transaction_id,

        -- Dates
        transaction_date::date                             as transaction_date,
        date_trunc('month', transaction_date::date)::date  as transaction_month,
        extract(year  from transaction_date::date)::int    as transaction_year,
        extract(quarter from transaction_date::date)::int  as transaction_quarter,

        -- Customer dimension
        lower(trim(customer_id))                           as customer_id,
        lower(trim(customer_email))                        as customer_email,
        initcap(trim(region))                              as region,
        initcap(trim(country))                             as country,

        -- Product dimension
        upper(trim(product_sku))                           as product_sku,
        initcap(trim(product_name))                        as product_name,
        initcap(trim(category))                            as category,

        -- Financial metrics
        round(amount::numeric, 2)                          as amount_usd,
        round(quantity::numeric, 0)::int                   as quantity,
        round((amount::numeric / nullif(quantity::numeric, 0)), 2) as unit_price,

        -- Status & flags
        lower(trim(status))                                as status,
        case
            when lower(status) = 'completed' then true
            else false
        end                                                as is_completed,
        case
            when lower(status) = 'refunded' then true
            else false
        end                                                as is_refunded,

        -- Audit columns
        created_at::timestamp                              as created_at,
        updated_at::timestamp                              as updated_at,
        current_timestamp                                  as dbt_loaded_at

    from source

    -- Remove soft-deleted records and obvious test data
    where is_deleted = false
      and customer_email not ilike '%test%'
      and amount::numeric > 0

)

select * from cleaned
