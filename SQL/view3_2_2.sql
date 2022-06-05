use ergasiadb;

CREATE VIEW projects_by_scientific_field AS
SELECT 
Scientific_Field.sf_name, Project.title 
FROM Scientific_Field
INNER JOIN SF_Of_Project ON Scientific_Field.id = SF_Of_Project.sf_id
INNER JOIN Project ON SF_Of_Project.pro_id = Project.id
ORDER BY Scientific_Field.sf_name