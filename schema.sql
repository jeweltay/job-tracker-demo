CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT,
    company_name TEXT NOT NULL,
    tags TEXT,
    position TEXT NOT NULL,
    location TEXT,
    date_applied TEXT,
    stage TEXT,
    response TEXT,
    career_fit_now INTEGER CHECK(career_fit_now BETWEEN 1 AND 5),
    interest_level INTEGER CHECK(interest_level BETWEEN 1 AND 5),
    growth_potential INTEGER CHECK(growth_potential BETWEEN 1 AND 5),
    salary_fit INTEGER CHECK(salary_fit BETWEEN 1 AND 5),
    total_score REAL,
    notes TEXT
);


