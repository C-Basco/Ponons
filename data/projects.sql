DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS tasks;

CREATE TABLE users (
    id SERIAL NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    first TEXT NOT NULL,
    last TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hashed_password VARCHAR(100) NOT NULL
);

CREATE TABLE projects (
    id SERIAL NOT NULL UNIQUE,
    title TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    owner_id INT NOT NULL REFERENCES users(id),
    member INT REFERENCES users(id)
);

CREATE TABLE tasks (
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    due_date DATE NOT NULL,
    is_completed BIT,
    project_id INT NOT NULL REFERENCES projects(id),
    assignee INT REFERENCES users(id)
);
