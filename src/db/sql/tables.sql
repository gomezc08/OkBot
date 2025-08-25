-- Drop tables if they exist
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS session_steps;
DROP TABLE IF EXISTS session_variables;
DROP TABLE IF EXISTS session_runs;

-- Create the sessions table
CREATE TABLE IF NOT EXISTS sessions (
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    version INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (name, version)
);

CREATE TABLE IF NOT EXISTS session_steps (
    session_name VARCHAR(255) NOT NULL,
    session_version INT NOT NULL,
    step_number INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    PRIMARY KEY(session_name, session_version, step_number),
    FOREIGN KEY (session_name, session_version) REFERENCES sessions(name, version)
);

CREATE TABLE IF NOT EXISTS session_variables (
    session_name VARCHAR(255) NOT NULL,
    session_version INT NOT NULL,
    variable_name VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,
    required BOOLEAN NOT NULL DEFAULT FALSE,
    requires_approval BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (session_name, session_version, variable_name),
    FOREIGN KEY (session_name, session_version) REFERENCES sessions(name, version)
);

CREATE TABLE IF NOT EXISTS session_runs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    session_name VARCHAR(255) NOT NULL,
    session_version INT NOT NULL,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME NULL,
    status ENUM('running', 'completed', 'failed', 'cancelled') NOT NULL DEFAULT 'running',
    log_path VARCHAR(500) NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (session_name, session_version) REFERENCES sessions(name, version),
    INDEX idx_session_name_version (session_name, session_version),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at)
);