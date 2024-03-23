
CREATE TABLE Employee (
  id_employee INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  service TEXT,
  hire_date DATE NOT NULL,
  id_user INTEGER,
  FOREIGN KEY (id_user) REFERENCES User(id_user) ON DELETE CASCADE
);


CREATE TABLE User (
  id_user INTEGER PRIMARY KEY AUTOINCREMENT,
  login VARCHAR(50) NOT NULL UNIQUE,
  hashed_password TEXT NOT NULL,
  is_hr BOOLEAN NOT NULL
);


CREATE TABLE VacationType (
  id_vacation_type INTEGER PRIMARY KEY AUTOINCREMENT,
  wording TEXT NOT NULL
);


CREATE TABLE VacationRequest (
  id_vacation_request INTEGER PRIMARY KEY AUTOINCREMENT,
  id_employee INTEGER NOT NULL,
  id_vacation_type INTEGER NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  number_days INTEGER NOT NULL CHECK (number_days > 0),
  status TEXT NOT NULL CHECK (status IN ('en attente', 'approuvee', 'rejetee')),
  FOREIGN KEY (id_employee) REFERENCES Employee(id_employee) ON DELETE CASCADE,
  FOREIGN KEY (id_vacation_type) REFERENCES VacationType(id_vacation_type) ON DELETE RESTRICT
);

CREATE TABLE VacationLeaveBalance (
  id_vacation INTEGER PRIMARY KEY AUTOINCREMENT,
  id_employee INTEGER NOT NULL,
  day_used_payed INTEGER,
  day_reduction_used INTEGER,
  day_acquired_payed INTEGER,
  day_reduction_acquired INTEGER,
  FOREIGN KEY (id_employee) REFERENCES Employee(id_employee) ON DELETE CASCADE
);

INSERT INTO Employee (first_name, name, email, service, hire_date, id_user) VALUES
('Alice', 'Martin', 'alice.martin@example.com', 'RH', '2023-01-01', 1),
('Bob', 'Dupont', 'bob.dupont@example.com', 'Marketing', '2022-05-15', 2),
('Charlie', 'Durand', 'charlie.durand@example.com', 'Informatique', '2021-12-01', 3),
('Diana', 'Lefevre', 'diana.lefevre@example.com', 'Commercial', '2020-08-24', 4);

INSERT INTO User (login, hashed_password, is_hr) VALUES
('alice.martin', 'f2d81a260dea8a100dd517984e53c56a7523d96942a834b9cdc249bd4e8c7aa9', false),
('bob.dupont', 'f2d81a260dea8a100dd517984e53c56a7523d96942a834b9cdc249bd4e8c7aa9', false),
('charlie.durand', 'f2d81a260dea8a100dd517984e53c56a7523d96942a834b9cdc249bd4e8c7aa9', false),
('diana.lefevre', 'f2d81a260dea8a100dd517984e53c56a7523d96942a834b9cdc249bd4e8c7aa9', true);

INSERT INTO VacationType (wording) VALUES
('Conges payes'),
('RTT');

INSERT INTO VacationRequest (id_employee, id_vacation_type, start_date, end_date, number_days, status) VALUES
(1, 2, '2024-03-20', '2024-03-25', 5, 'en attente'),
(2, 1, '2024-04-01', '2024-04-01', 1, 'approuvee'),
(3, 2, '2024-02-10', '2024-02-15', 5, 'rejetee'),
(4, 1, '2024-05-10', '2024-06-05', 20, 'en attente');

INSERT INTO VacationLeaveBalance (id_employee, day_used_payed, day_reduction_used, day_acquired_payed, day_reduction_acquired) VALUES
(1, 10, 1, 25, 10),
(2, 8, 4, 12, 8),
(3, 15, 2, 32, 8),
(4, 15, 0, 36, 15);

