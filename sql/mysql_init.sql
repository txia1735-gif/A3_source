CREATE DATABASE IF NOT EXISTS ai_learning_agent
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE ai_learning_agent;

CREATE TABLE IF NOT EXISTS user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  email VARCHAR(120) NOT NULL UNIQUE,
  grade VARCHAR(50) NULL,
  major VARCHAR(100) NULL,
  bio TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS user_profile (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  dimensions JSON NOT NULL,
  weights JSON NOT NULL,
  refresh_suggestions JSON NOT NULL,
  last_conversation TEXT NULL,
  last_study_topic VARCHAR(255) NULL,
  memory_strength DECIMAL(5,4) NOT NULL DEFAULT 1.0000,
  last_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_user_profile_user_id UNIQUE (user_id),
  CONSTRAINT fk_user_profile_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS learning_resource (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  topic VARCHAR(255) NOT NULL,
  resource_type VARCHAR(50) NOT NULL,
  description TEXT NOT NULL,
  content LONGTEXT NOT NULL,
  metadata_json JSON NOT NULL,
  file_path VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_learning_resource_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  INDEX idx_learning_resource_user_id (user_id),
  INDEX idx_learning_resource_topic (topic),
  INDEX idx_learning_resource_type (resource_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS study_path (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  topic VARCHAR(255) NOT NULL,
  target_days INT NOT NULL DEFAULT 7,
  status VARCHAR(30) NOT NULL DEFAULT 'active',
  path_nodes JSON NOT NULL,
  recommendations JSON NOT NULL,
  progress DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_study_path_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  INDEX idx_study_path_user_id (user_id),
  INDEX idx_study_path_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS qa_record (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  question TEXT NOT NULL,
  answer LONGTEXT NOT NULL,
  topic VARCHAR(255) NULL,
  answer_type VARCHAR(50) NOT NULL DEFAULT 'text',
  confidence DECIMAL(5,4) NOT NULL DEFAULT 0.8000,
  metadata_json JSON NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_qa_record_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  INDEX idx_qa_record_user_id (user_id),
  INDEX idx_qa_record_topic (topic)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS evaluate_report (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  report_period VARCHAR(100) NOT NULL,
  overall_score DECIMAL(5,2) NOT NULL,
  dimension_scores JSON NOT NULL,
  summary TEXT NOT NULL,
  optimization_actions JSON NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_evaluate_report_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  INDEX idx_evaluate_report_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
