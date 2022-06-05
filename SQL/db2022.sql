DROP DATABASE IF EXISTS ergasiadb;

CREATE DATABASE IF NOT EXISTS ergasiadb;
USE ergasiadb;

create table if not exists Organisation(
	id INT NOT NULL auto_increment primary key,
    org_name VARCHAR(50) NOT NULL,
	abbreviation  VARCHAR(10) NOT NULL,
    address_postal_code VARCHAR(50),
    address_street VARCHAR(50) NOT null,
    address_city VARCHAR(50) NOT NULL        
);

create table if not exists Program(
	id INT NOT NULL auto_increment primary key,
    program_name VARCHAR(50) NOT NULL,
	address VARCHAR(50) NOT NULL      
    );

create table if not exists Executive(
	id INT NOT NULL auto_increment primary key,
    executive_name VARCHAR(50) NOT NULL
    );
    
create table if not exists Company(
	id INT NOT NULL primary key UNIQUE, 
    private_funds INT(5) NOT NULL,
    foreign key(id) references Organisation(id) ON DELETE CASCADE
    );
    
create table if not exists University(
	id INT NOT NULL primary key UNIQUE, 
    budget INT(5) NOT NULL ,
    foreign key(id) references Organisation(id) ON DELETE CASCADE
    );
    
create table if not exists Research_Center(
	id INT NOT NULL primary key UNIQUE, 
    private_funds INT(5) NOT NULL ,
	budget INT(5) NOT NULL ,
    foreign key(id) references Organisation(id) ON DELETE CASCADE
    );
    

create table if not exists Researcher(
	id INT NOT NULL auto_increment primary key,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth date NOT NULL,
    gender VARCHAR(50),
    org_id INT,
    foreign key(org_id) references Organisation(id) ON DELETE SET NULL
    );
    
create table if not exists Evaluation(
	id INT NOT NULL auto_increment primary key, 
    grade INT NOT NULL ,
	ev_date date NOT NULL ,
    researcher_id INT NOT NULL UNIQUE,
    foreign key(researcher_id) references Researcher(id) ON DELETE CASCADE
    );
    
create table if not exists Project(
	id INT NOT NULL auto_increment primary key, 
    title VARCHAR(50) NOT NULL UNIQUE,
    summary text(1000) NOT NULL, 
	date_start date NOT NULL ,
	date_end date NOT NULL,
    amount INT(7) NOT NULL , 
    organisation_id INT NOT NULL,
    foreign key(organisation_id) references Organisation(id)  ON DELETE CASCADE,
    program_id INT,
    foreign key(program_id) references Program(id) ON DELETE SET NULL,
    executive_id INT UNIQUE,
    foreign key(executive_id) references Executive(id) ON DELETE SET NULL,
    evaluation_id INT UNIQUE,
    foreign key(evaluation_id) references Evaluation(id) ON DELETE SET NULL
    );
    
create table if not exists Scientific_Field(
	id INT NOT NULL auto_increment primary key, 
    sf_name VARCHAR(50)
    );
    
create table if not exists SF_Of_Project(
	id int not null auto_increment primary key,
	sf_id INT NOT NULL, 
	foreign key(sf_id) references Scientific_Field(id)  ON DELETE CASCADE,
    pro_id INT NOT NULL,
	foreign key(pro_id) references Project(id)  ON DELETE CASCADE
    );
    

create table if not exists Works_On(
	project_id INT NOT NULL,
    researcher_id INT NOT NULL,
    primary key (project_id, researcher_id),
    foreign key (project_id) references Project(id)  ON DELETE CASCADE,
    foreign key (researcher_id) references Researcher(id)  ON DELETE CASCADE
);

create table Deliverable(
	id INT NOT NULL auto_increment primary key,
    project_id INT NOT NULL,
    foreign key (project_id) references Project(id)  ON DELETE CASCADE,
	title VARCHAR(100) NOT NULL,
    summary text(1000) NOT NULL
);



/* Views */

CREATE OR REPLACE VIEW v3_2_1 AS
SELECT 
Project.title, Researcher.last_name, Researcher.first_name 
FROM Researcher
INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
INNER JOIN Project ON Works_On.project_id = Project.id
ORDER BY Researcher.last_name;



CREATE OR REPLACE VIEW v3_2_2 AS
SELECT Executive.executive_name exname, sum(Project.amount) as amount
FROM Executive 
INNER JOIN Project ON Executive.id = Project.executive_id
GROUP BY exname
ORDER BY exname;

    
    
    

/* Constraints and Triggers */



ALTER TABLE Project
ADD COLUMN duration FLOAT AS (round(DATEDIFF(date_end, date_start)/365, 1));


ALTER TABLE Researcher
ADD COLUMN age INT AS (FLOOR(DATEDIFF('2022-6-5', date_of_birth)/365));


ALTER TABLE Project
ADD CONSTRAINT amount_check CHECK(amount BETWEEN 100000 AND 1000000);

ALTER TABLE Project
ADD CONSTRAINT duration_check CHECK(duration BETWEEN 1.0 AND 4.0);


CREATE OR REPLACE VIEW researchers_on_project 
AS SELECT Researcher.id AS rid, Project.id AS pid, Project.evaluation_id AS evid
FROM Researcher 
INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
INNER JOIN  Project ON Project.id = Works_On.project_id;


CREATE TABLE evaluation_check AS
SELECT Evaluation.researcher_id AS evaluator_id, researchers_on_project.rid AS rid
FROM researchers_on_project 
INNER JOIN Evaluation ON researchers_on_project.evid = Evaluation.id
ORDER BY evaluator_id;






/* Views */


CREATE OR REPLACE VIEW projects_by_researcher AS
SELECT 
Project.title, Researcher.last_name, Researcher.first_name 
FROM Researcher
INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
INNER JOIN Project ON Works_On.project_id = Project.id
ORDER BY Researcher.last_name;

CREATE VIEW projects_by_scientific_field AS
SELECT 
Scientific_Field.sf_name, Project.title 
FROM Scientific_Field
INNER JOIN SF_Of_Project ON Scientific_Field.id = SF_Of_Project.sf_id
INNER JOIN Project ON SF_Of_Project.pro_id = Project.id
ORDER BY Scientific_Field.sf_name;



-- DELIMITER $$
-- CREATE TRIGGER insert_into_evaluation
-- BEFORE INSERT ON Evaluation
-- FOR EACH ROW
-- BEGIN
-- 	INSERT INTO evaluation_check (evaluator_id, rid) VALUES (new.researcher_id, new.id);
-- END$$
--     DELIMITER ;
--     
--     
-- DELIMITER $$
-- CREATE TRIGGER update_evaluation
-- BEFORE INSERT ON Evaluation
-- FOR EACH ROW
-- BEGIN
-- 	UPDATE evaluation_check SET evaluator_id = new.researcher_id WHERE (rid = new.id);
-- END$$
--     DELIMITER ;
--     
    
-- ALTER TABLE evaluation_check
-- ADD CONSTRAINT ev_check1 CHECK (evaluator_id <> rid);


-- DELIMITER $$
-- CREATE TRIGGER ev_check2
-- BEFORE INSERT ON Evaluation
-- FOR EACH ROW
-- BEGIN
--   IF EXISTS (SELECT Evaluation.ev_date, Project.date_end FROM Evaluation INNER JOIN Project ON Project.evaluation_id = Evaluation.id WHERE Evaluation.ev_date < Project.date_end)
--   THEN
--   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Warning: Evaluation must take place after Project ends!';
--   END IF;

-- END$$
--     DELIMITER ;
--     
-- DELIMITER $$
-- CREATE TRIGGER ev_check3
-- BEFORE UPDATE ON Evaluation
-- FOR EACH ROW
-- BEGIN
--   IF EXISTS (SELECT Evaluation.NEW.ev_date, Project.date_end FROM Evaluation INNER JOIN Project ON Project.evaluation_id = Evaluation.id WHERE Evaluation.NEW.ev_date < Project.date_end)
--   THEN
--   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Warning: Evaluation must take place after Project ends!';
--   END IF;

-- END$$
--     DELIMITER ;


/* Indexes */

CREATE INDEX index_id ON Project(id);
CREATE INDEX index_project_title ON Project(title);
CREATE INDEX index_date_start ON Project(date_start);
CREATE INDEX index_sf ON Scientific_Field(id);
CREATE INDEX index_id ON Researcher(id);