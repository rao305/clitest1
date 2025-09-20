-- Purdue CS Curriculum Database Schema

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(300) NOT NULL,
    credits INTEGER DEFAULT 0,
    description TEXT,
    category VARCHAR(50) DEFAULT 'elective',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracks table
CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    objectives TEXT,
    min_electives INTEGER DEFAULT 0,
    total_credits INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track requirements table
CREATE TABLE IF NOT EXISTS track_requirements (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
    course_code VARCHAR(20) REFERENCES courses(code) ON DELETE CASCADE,
    requirement_type VARCHAR(20) CHECK (requirement_type IN ('required', 'elective')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prerequisites table
CREATE TABLE IF NOT EXISTS prerequisites (
    id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) REFERENCES courses(code) ON DELETE CASCADE,
    prerequisite_code VARCHAR(20) REFERENCES courses(code) ON DELETE CASCADE,
    requirement_type VARCHAR(20) DEFAULT 'mandatory',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scraping logs table
CREATE TABLE IF NOT EXISTS scraping_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    courses_scraped INTEGER DEFAULT 0,
    tracks_scraped INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    details JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(code);
CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category);
CREATE INDEX IF NOT EXISTS idx_track_requirements_track ON track_requirements(track_id);
CREATE INDEX IF NOT EXISTS idx_track_requirements_course ON track_requirements(course_code);
CREATE INDEX IF NOT EXISTS idx_prerequisites_course ON prerequisites(course_code);
CREATE INDEX IF NOT EXISTS idx_prerequisites_prereq ON prerequisites(prerequisite_code);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_timestamp ON scraping_logs(timestamp);

-- Insert default tracks
INSERT INTO tracks (name, display_name, objectives, min_electives, total_credits) 
VALUES 
    ('machine_intelligence', 'Machine Intelligence', 'Prepare students for careers in artificial intelligence, machine learning, and data science', 3, 9),
    ('software_engineering', 'Software Engineering', 'Prepare students for careers in software development, systems architecture, and engineering management', 2, 8)
ON CONFLICT (name) DO NOTHING;
