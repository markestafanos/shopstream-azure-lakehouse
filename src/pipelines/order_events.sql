CREATE OR REFRESH STREAMING TABLE order_events (
  CONSTRAINT valid_quantity EXPECT (quantity > 0) ON VIOLATION DROP ROW,
  CONSTRAINT has_keys EXPECT (order_id IS NOT NULL AND customer_id IS NOT NULL
                              AND product_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT known_status EXPECT (status IN ('completed', 'cancelled'))
)
COMMENT 'Live ShopStream order events, loaded with Auto Loader'
AS SELECT
  event_id, order_id, customer_id, product_id,
  CAST(quantity AS INT)      AS quantity,
  CAST(unit_price AS DOUBLE) AS unit_price,
  status,
  CAST(event_ts AS TIMESTAMP) AS event_ts,
  _metadata.file_path        AS _source_file,
  current_timestamp()        AS _ingested_at
FROM STREAM read_files('/Volumes/${catalog}/bronze/events/orders_stream', format => 'json');

CREATE OR REFRESH MATERIALIZED VIEW shopstream_dev.silver.order_events
COMMENT 'Live orders, deduplicated and shaped like silver.orders'
AS SELECT
  order_id, customer_id, product_id, quantity, unit_price,
  ROUND(quantity * unit_price, 2) AS line_revenue,
  status,
  event_ts AS order_ts
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY _ingested_at) AS rn
  FROM order_events
)
WHERE rn = 1;