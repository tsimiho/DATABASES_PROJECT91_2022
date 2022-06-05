use ergasiadb;

CREATE OR REPLACE VIEW projects_by_researcher AS
SELECT 
Project.title, Researcher.last_name, Researcher.first_name 
FROM Researcher
INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
INNER JOIN Project ON Works_On.project_id = Project.id
ORDER BY Researcher.last_name