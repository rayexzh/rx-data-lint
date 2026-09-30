CREATE TABLE source (
 id INTEGER PRIMARY KEY, filename TEXT NOT NULL, source_url TEXT NOT NULL,
 sha256 TEXT NOT NULL, checked_at_utc TEXT NOT NULL, row_count INTEGER NOT NULL
);
CREATE TABLE records (
 row_number INTEGER PRIMARY KEY, source_id INTEGER NOT NULL REFERENCES source(id),
 month TEXT, ods_code TEXT, product_code TEXT, product_name TEXT,
 cost_gbp REAL, cost_status TEXT NOT NULL CHECK(cost_status IN ('known','missing','invalid')),
 quantity_udfs REAL, unit_udfs TEXT, raw_json TEXT NOT NULL
);
CREATE TABLE findings (
 id INTEGER PRIMARY KEY, rule TEXT NOT NULL, severity TEXT NOT NULL,
 row_number INTEGER REFERENCES records(row_number), column_name TEXT, message TEXT
);
CREATE INDEX records_month_product ON records(month, product_code);
CREATE INDEX findings_row ON findings(row_number);
