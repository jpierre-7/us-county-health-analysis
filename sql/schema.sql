CREATE TABLE county (
    fipscode VARCHAR(5) PRIMARY KEY,
    state_name VARCHAR(255),
    county_name VARCHAR(255)
);

CREATE TABLE measure (
    measure_id INTEGER PRIMARY KEY,
    measure_name VARCHAR(255) NOT NULL
);

CREATE TABLE fact_observations (
    id SERIAL PRIMARY KEY,
    fipscode VARCHAR(5) NOT NULL,
    measure_id INTEGER NOT NULL,
    year_start INTEGER,
    year_end INTEGER,
    numerator FLOAT,
    denominator FLOAT,
    raw_value FLOAT,
    ci_lower FLOAT,
    ci_upper FLOAT,
    data_release_year INTEGER,
    FOREIGN KEY (fipscode) REFERENCES county(fipscode),
    FOREIGN KEY (measure_id) REFERENCES measure(measure_id)
);