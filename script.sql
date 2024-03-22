DROP TABLE IF EXISTS Employee;
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

DROP TABLE IF EXISTS User;
CREATE TABLE User (
  id_user INTEGER PRIMARY KEY AUTOINCREMENT,
  login VARCHAR(50) NOT NULL UNIQUE,
  hashed_password TEXT NOT NULL
);

DROP TABLE IF EXISTS VacationType;
CREATE TABLE VacationType (
  id_vacation_type INTEGER PRIMARY KEY AUTOINCREMENT,
  wording TEXT NOT NULL
);

DROP TABLE IF EXISTS VacationRequest;
CREATE TABLE VacationRequest (
  id_vacation_request INTEGER PRIMARY KEY AUTOINCREMENT,
  id_employee INTEGER NOT NULL,
  id_vacation_type INTEGER NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  number_days INTEGER NOT NULL CHECK (number_days > 0),
  status TEXT NOT NULL CHECK (status IN ('en attente', 'approuvee', 'rejetee')),
  request_date DATE NOT NULL,
  FOREIGN KEY (id_employee) REFERENCES Employee(id_employee) ON DELETE CASCADE,
  FOREIGN KEY (id_vacation_type) REFERENCES VacationType(id_vacation_type) ON DELETE RESTRICT
);

DROP TABLE IF EXISTS VacationValidation;
CREATE TABLE VacationValidation (
  id_validation INTEGER PRIMARY KEY AUTOINCREMENT,
  id_vacation_request INTEGER NOT NULL,
  id_employee INTEGER,
  validation_date DATE NOT NULL,
  FOREIGN KEY (id_vacation_request) REFERENCES VacationRequest(id_vacation_request) ON DELETE CASCADE,
  FOREIGN KEY (id_employee) REFERENCES Employee(id_employee) ON DELETE RESTRICT
);

DROP TABLE IF EXISTS VacationLeaveBalance;
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

INSERT INTO User (login, hashed_password) VALUES
('alice.martin', 'f2d81a260dea8a100dd517984e53c56a7523d96942a834b9cdc249bd4e8c7aa9'),
('bob.dupont', 'f2d81a260dea8a100dd517984e53c56a7523d96942a834b9cdc249bd4e8c7aa9'),
('charlie.durand', '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'),
('diana.lefevre', '11a4a60b518bf24989d481468076e5d5982884626aed9faeb35b8576fcd223e1');

INSERT INTO VacationType (wording) VALUES
('Conges payes'),
('RTT');

INSERT INTO VacationRequest (id_employee, id_vacation_type, start_date, end_date, number_days, status, request_date) VALUES
(1, 2, '2024-03-20', '2024-03-25', 5, 'en attente', '2024-02-15'),
(2, 1, '2024-04-01', '2024-04-01', 1, 'approuvee', '2024-03-08'),
(3, 2, '2024-02-10', '2024-02-15', 5, 'rejetee', '2024-01-30'),
(4, 1, '2024-05-10', '2024-06-05', 20, 'en attente', '2024-03-10');

INSERT INTO VacationValidation (id_vacation_request, id_employee, validation_date) VALUES
(2, 1, '2024-03-12'),
(3, 2, '2024-02-05');

INSERT INTO VacationLeaveBalance (id_employee, day_used_payed, day_reduction_used, day_acquired_payed, day_reduction_acquired) VALUES
(1, 10, 1, 25, 10),
(2, 8, 4, 12, 8),
(3, 15, 2, 32, 8),
(4, 15, 0, 36, 15);

