-- Task Management schema
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    status      TEXT    NOT NULL CHECK (status IN ('todo','in_progress','done','cancelled')),
    priority    TEXT    NOT NULL CHECK (priority IN ('low','medium','high','urgent')),
    dueDate     TEXT    NOT NULL,   -- ISO 8601: YYYY-MM-DD
    assignedID  INTEGER NOT NULL
);

-- Index hỗ trợ keyset pagination & filter
CREATE INDEX IF NOT EXISTS idx_tasks_status     ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority   ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_assignedID ON tasks(assignedID);
CREATE INDEX IF NOT EXISTS idx_tasks_dueDate    ON tasks(dueDate);
CREATE INDEX IF NOT EXISTS idx_tasks_id         ON tasks(id);


-- Seed khởi tạo
INSERT INTO tasks (title, status, priority, dueDate, assignedID) VALUES
    ('Fix login bug',            'in_progress', 'high',   '2025-12-31', 1),
    ('Write unit tests',         'todo',        'medium', '2025-12-15', 2),
    ('Refactor auth module',     'todo',        'low',    '2026-01-10', 1),
    ('Update API docs',          'done',        'low',    '2025-11-30', 3),
    ('Migrate to Postgres',      'todo',        'urgent', '2026-02-01', 2),
    ('Fix pagination cursor',    'in_progress', 'high',   '2025-12-20', 3),
    ('Code review PR #42',       'done',        'medium', '2025-12-05', 1),
    ('Setup CI pipeline',        'todo',        'high',   '2026-01-05', 4),
    ('Audit security logs',      'cancelled',   'low',    '2025-12-01', 2),
    ('Design dashboard UI',      'in_progress', 'medium', '2026-01-20', 4),
    ('Optimize slow query',      'todo',        'high',   '2025-12-25', 1),
    ('Add rate limiting',        'todo',        'medium', '2026-01-15', 3),
    ('Write onboarding guide',   'done',        'low',    '2025-11-20', 2),
    ('Upgrade dependencies',     'todo',        'low',    '2026-03-01', 4),
    ('Implement 2FA',            'in_progress', 'urgent', '2026-02-10', 1);