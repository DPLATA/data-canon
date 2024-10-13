-- Create the departments table
CREATE TABLE departments (
    id INT PRIMARY KEY,
    department VARCHAR(100) NOT NULL
);

-- Create the jobs table
CREATE TABLE jobs (
    id INT PRIMARY KEY,
    job VARCHAR(100) NOT NULL
);

-- Create the employees table
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hire_datetime DATETIME NOT NULL,
    department_id INT NOT NULL,
    job_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Create indexes for better query performance
CREATE INDEX idx_employee_department ON employees(department_id);
CREATE INDEX idx_employee_job ON employees(job_id);