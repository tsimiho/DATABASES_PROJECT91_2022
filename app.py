import re
from flask import Flask, render_template, request, redirect, url_for, flash, g, session
from flask_mysqldb import MySQL
# import yaml

tables = ["Organisation", "Program", "Executive", "Company", "University", "Research_Center", "Researcher", "Evaluation", "Project", "Scientific_Field", "Deliverable"]
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='TheBoss', password='password'))



app = Flask(__name__,static_url_path="", static_folder="static")
app.secret_key = 'somesecretkeythatonlyishouldknow'

# Configure db
# db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'database2001'
app.config['MYSQL_DB'] = 'ergasiadb'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/programs')
def programs():
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT program_name, id, address FROM Program")
    programs = cur1.fetchall()
    return render_template('programs.html',programDetails=programs)





@app.route('/projects')
def projects():
    cur2 = mysql.connection.cursor()
    cur2.execute("""
    SELECT Project.title AS title, Project.date_start AS date_start, Project.date_end AS date_end, Project.duration AS duration, YEAR(Project.date_start) as year_start, Executive.executive_name AS ex_name, Project.id AS id 
    FROM Project 
    INNER JOIN Executive on Project.executive_id = Executive.id
    ORDER BY title   
    """)
    projects = cur2.fetchall()


    # cur4 = mysql.connection.cursor()
    # resultValue4 = cur4.execute(f"""
    # CREATE OR REPLACE VIEW project_researcher AS
    # SELECT 
    # Project.id AS id, Project.title AS title, CONCAT(Researcher.last_name, ' ', Researcher.first_name) AS full_name 
    # FROM Researcher
    # INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
    # INNER JOIN Project ON Works_On.project_id = Project.id
    # ORDER BY Project.title
    # """)
    # researchersOnProjects = cur4.fetchall()

    return render_template('base.html', projectDetails = projects)



@app.route('/projects/<id>')
def project_researchers(id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
    SELECT 
    CONCAT(Researcher.last_name, ' ', Researcher.first_name) AS full_name, Project.title 
    FROM Researcher
    INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
    INNER JOIN Project ON Works_On.project_id = Project.id
    WHERE Project.id = {id}
    ORDER BY Project.title
    """)
    result = cur.fetchall()

    return render_template('project_researchers.html', result = result)


@app.route('/more')
def more():
    return render_template('more.html')

@app.route('/3_2_1')
def q3_2_1():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE OR REPLACE VIEW test AS
    SELECT 
    Project.title, Researcher.last_name, Researcher.first_name 
    FROM Researcher
    INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
    INNER JOIN Project ON Works_On.project_id = Project.id
    ORDER BY Researcher.last_name;
    """)

    cur.execute("""
    SELECT * FROM test;
    """)
    v = cur.fetchall()


    return render_template('q3_2_1.html', v = v)


@app.route('/3_2_2')
def q3_2_2():
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT * FROM v3_2_2
    """)
    v = cur.fetchall()


    return render_template('q3_2_2.html', v = v)


@app.route('/3_3')
def q3_3():

    cur = mysql.connection.cursor()
    
    cur.execute("""
    CREATE OR REPLACE VIEW v1 AS
    SELECT 
    Scientific_Field.sf_name as sf,  Project.title as pt
    FROM Scientific_Field
    INNER JOIN SF_Of_Project ON Scientific_Field.id = SF_Of_Project.sf_id
    INNER JOIN Project ON SF_Of_Project.pro_id = Project.id
    WHERE (CURRENT_DATE() < Project.date_end);
     """)


    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE OR REPLACE VIEW v2 AS
    SELECT distinct
    Scientific_Field.sf_name as sf, Researcher.last_name as ln
    FROM Scientific_Field
    INNER JOIN SF_Of_Project ON Scientific_Field.id = SF_Of_Project.sf_id
    INNER JOIN Project ON SF_Of_Project.pro_id = Project.id
    INNER JOIN Works_On ON Works_On.project_id = Project.id
    INNER JOIN Researcher ON Works_On.researcher_id = Researcher.id
    WHERE (CURRENT_DATE() > Project.date_start);
    """)

    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT 
    v1.sf, v1.pt, v2.ln
    FROM v1
    INNER JOIN v2 ON v1.sf = v2.sf
    ORDER BY v1.sf
    """)
    sfield = cur.fetchall()

    cur.execute("""
    drop table if exists v1;
    drop table if exists v2;
    """)
   

    return render_template('sf.html', sfield = sfield)



@app.route('/3_4')
def q3_4():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE OR REPLACE VIEW projects_by_org (oid, org_name, projects, year_start) AS
    SELECT Organisation.id, Organisation.org_name, count(*), YEAR(Project.date_start)
    FROM Project
    INNER JOIN Organisation ON Project.organisation_id = Organisation.id
    GROUP BY Organisation.id, YEAR(Project.date_start);

    SELECT p1.oid, p1.org_name, p1.year_start as first_year, p2.year_start AS second_year, p1.projects AS pey 
    FROM projects_by_org p1, projects_by_org p2
    WHERE p1.oid = p2.oid AND p1.year_start = p2.year_start - 1 AND p1.projects = p2.projects AND p1.projects > 0 AND p2.projects > 0;
    """)

    p = cur.fetchall()

    return render_template('projects_by_org.html', p = p)




@app.route('/3_5')
def q3_5():
    cur = mysql.connection.cursor()

    cur.execute("""
    CREATE OR REPLACE VIEW SF_Projects AS
    SELECT Scientific_Field.sf_name AS Scientific_Field_Name, Project.title as Project_Title, Project.id AS p_id, Scientific_Field.id AS sfid
    FROM Scientific_Field
    INNER JOIN SF_Of_Project On Scientific_Field.id = SF_Of_Project.sf_id
    INNER JOIN Project ON SF_Of_Project.pro_id = Project.id
    ORDER BY Project.title;
    """)

    cur.execute("""
    CREATE OR REPLACE VIEW pairs AS
    SELECT sf1.p_id, sf1.Project_Title AS title, CONCAT(sf1.Scientific_Field_Name, ' and ', sf2.Scientific_Field_Name) AS sfs
    FROM SF_Projects as sf1
    CROSS JOIN SF_Projects as sf2
    WHERE sf1.p_id = sf2.p_id AND sf1.sfid > sf2.sfid
    ORDER BY sf1.p_id
    """)

    cur.execute("""
    SELECT sfs, count(title) AS total_projects FROM pairs GROUP BY sfs LIMIT 3;
    """)
    sf = cur.fetchall()

    return render_template('sf_of_project.html', sf = sf)


@app.route('/3_6')
def q3_6():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE OR REPLACE VIEW researcher_project AS
    SELECT Researcher.id AS id, Project.title as title
    FROM Researcher
    INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
    INNER JOIN Project ON Project.id = Works_On.researcher_id
    WHERE (DATEDIFF(CURRENT_DATE(), Project.date_end) < 0) AND Researcher.age < 40;

    CREATE OR REPLACE VIEW projects_per_researcher AS
    SELECT id, count(title) as project_count
    FROM researcher_project
    GROUP BY id;
    """)

    cur.execute("""
    SELECT projects_per_researcher.project_count AS pc, CONCAT(Researcher.last_name, ' ', Researcher.first_name) AS fn, Researcher.age AS age
    FROM projects_per_researcher
    INNER JOIN Researcher ON Researcher.id = projects_per_researcher.id
    ORDER BY pc
    """)
    result = cur.fetchall()

    return render_template('q3_6.html', result = result)


@app.route('/3_7')
def q3_7():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE OR REPLACE VIEW comps AS
    SELECT Organisation.id as comps_id, Organisation.org_name as comps_name
    FROM Organisation 
    INNER JOIN Company ON Organisation.id = Company.id;

    CREATE OR REPLACE VIEW epo AS
    SELECT Executive.id AS epo_id, Executive.executive_name exname, Project.amount as amount
    FROM Executive 
    INNER JOIN Project ON Executive.id = Project.executive_id
    ORDER BY exname;

    """)

    cur.execute("""
    SELECT Executive.executive_name, comps.comps_name, epo.amount
    from epo
    INNER JOIN Executive ON epo.epo_id = Executive.id
    INNER JOIN Project ON Executive.id = Project.executive_id
    INNER JOIN comps ON Project.organisation_id = comps.comps_id
    ORDER BY epo.amount DESC
    LIMIT 5;
    """)
    result = cur.fetchall()


    return render_template('q3_7.html', result = result)



@app.route('/3_8')
def q3_8():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE OR REPLACE VIEW projects_with_deliverbles AS
    SELECT DISTINCT Project.id, Project.title AS title
    FROM Project
    INNER JOIN Deliverable on Project.id = Deliverable.project_id;

    
    CREATE OR REPLACE VIEW projects_without_deliverbles AS
    SELECT DISTINCT Project.id as pwd_id, Project.title
    FROM Project
    WHERE NOT EXISTS (SELECT * FROM projects_with_deliverbles WHERE projects_with_deliverbles.id = Project.id);


    CREATE OR REPLACE VIEW researcher_project AS
    SELECT CONCAT(Researcher.first_name, ' ', Researcher.last_name) as fn, Project.title as title, Project.id as rp_id
    FROM Researcher
    INNER JOIN Works_On ON Researcher.id = Works_On.researcher_id
    INNER JOIN Project ON Project.id = Works_On.researcher_id
    ORDER BY fn;


    CREATE OR REPLACE VIEW researcher_without_deliverables AS
    SELECT researcher_project.fn AS fn, researcher_project.title AS title
    FROM researcher_project
    INNER JOIN projects_without_deliverbles ON researcher_project.rp_id = projects_without_deliverbles.pwd_id;

    CREATE OR REPLACE VIEW researcher_without_deliverables_total AS
    SELECT fn, count(title) as total
    FROM researcher_without_deliverables
    GROUP BY fn
    """)

    cur.execute("""
    SELECT * FROM researcher_without_deliverables_total WHERE (total >= 5)
    """)
    result = cur.fetchall()

    return render_template('q3_8.html', result = result)


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('crud'))

        return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/crud')
def crud():
    if not g.user:
        return redirect(url_for('login'))
    
    return render_template('crud.html', t = tables)   #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



@app.route('/Organisation_add', methods = ['GET','POST'])
def insert_org():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Organisation")
        result = cur.fetchall()
        return render_template("insert_org.html", result = result)
    if request.method == 'POST':
        org_name = request.form["org_name"]
        abbreviation = request.form["abbreviation"]
        address_postal_code = request.form["address_postal_code"]
        address_street = request.form["address_street"]
        address_city = request.form["address_city"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Organisation (org_name, abbreviation, address_postal_code, address_street, address_city) VALUES (%s, %s, %s, %s, %s)", (org_name, abbreviation, address_postal_code, address_street, address_city))
        con.commit()
        return redirect(url_for('insert_org'))


@app.route('/Organisation_edit', methods = ['GET','POST'])
def update_org():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Organisation")
        result = cur.fetchall()
        return render_template("update_org.html", result = result)
    if request.method == 'POST':
        id = request.form["id"]
        org_name = request.form["org_name"]
        abbreviation = request.form["abbreviation"]
        address_postal_code = request.form["address_postal_code"]
        address_street = request.form["address_street"]
        address_city = request.form["address_city"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE  Organisation SET org_name = %s, abbreviation = %s, address_postal_code = %s, address_street = %s, address_city = %s WHERE id = %s", (org_name, abbreviation, address_postal_code, address_street, address_city, id))
        con.commit()
        return redirect(url_for('update_org'))


@app.route('/Organisation_del', methods = ['GET','POST'])
def delete_org():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Organisation")
        result = cur.fetchall()
        return render_template("delete_org.html", result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Organisation" ,result = result)
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Organisation WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_org'))



@app.route('/Program_add', methods = ['GET','POST'])
def insert_prog():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Program")
        result = cur.fetchall()
        return render_template("insert_prog.html",result = result)
    if request.method == 'POST':
        program_name = request.form["program_name"]
        address = request.form["address"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Program (program_name, address) VALUES (%s, %s)", (program_name, address))
        con.commit()
        return redirect(url_for('insert_prog'))



@app.route('/Program_edit', methods = ['GET','POST'])
def update_prog():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Program")
        result = cur.fetchall()
        return render_template("update_prog.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        program_name = request.form["program_name"]
        address = request.form["address"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE Program SET program_name = %s, address = %s WHERE id = %s", (program_name, address, id))
        con.commit()
        return redirect(url_for('update_prog'))



@app.route('/Program_del', methods = ['GET','POST'])
def delete_prog():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Program")
        result = cur.fetchall()
        return render_template("delete_prog.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Program")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Program WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_prog'))


@app.route('/Executive_add', methods = ['GET','POST'])
def insert_exe():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Executive")
        result = cur.fetchall()
        return render_template("insert_exe.html",result = result)
    if request.method == 'POST':
        executive_name = request.form["executive_name"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Executive (executive_name) VALUES (%s)", (executive_name,))
        con.commit()
        return redirect(url_for('insert_exe'))



@app.route('/Executive_edit', methods = ['GET','POST'])
def update_exe():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Executive")
        result = cur.fetchall()
        return render_template("update_exe.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        executive_name = request.form["executive_name"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE Executive SET executive_name = %s WHERE id = %s", (executive_name, id))
        con.commit()
        return redirect(url_for('update_exe'))


@app.route('/Executive_del', methods = ['GET','POST'])
def delete_exe():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Executive")
        result = cur.fetchall()
        return render_template("delete_exe.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Executive")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Executive WHERE id = %s", id)
        con.commit()
        return redirect(url_for('delete_exe'))



@app.route('/Company_add', methods = ['GET','POST'])
def insert_comp():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Company")
        result = cur.fetchall()
        return render_template("insert_comp.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        private_funds = request.form["private_funds"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Company (id, private_funds) VALUES (%s, %s)", (id, private_funds))
        con.commit()
        return redirect(url_for('insert_comp'))


@app.route('/Company_edit', methods = ['GET','POST'])
def update_comp():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Company")
        result = cur.fetchall()
        return render_template("update_comp.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        private_funds = request.form["private_funds"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE Executive SET private_funds = %s WHERE id = %s", (private_funds, id))
        con.commit()
        return redirect(url_for('update_comp'))


@app.route('/Company_del', methods = ['GET','POST'])
def delete_comp():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Company")
        result = cur.fetchall()
        return render_template("delete_comp.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Company")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Company WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_comp'))



@app.route('/University_add', methods = ['GET','POST'])
def insert_uni():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM University")
        result = cur.fetchall()
        return render_template("insert_uni.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        budget = request.form["budget"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO University (id, budget) VALUES (%s, %s)", (id, budget))
        con.commit()
        return redirect(url_for('insert_uni'))


@app.route('/University_edit', methods = ['GET','POST'])
def update_uni():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM University")
        result = cur.fetchall()
        return render_template("update_uni.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        budget = request.form["budget"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE University SET budget = %s WHERE id = %s", (budget, id))
        con.commit()
        return redirect(url_for('update_uni'))


@app.route('/University_del', methods = ['GET','POST'])
def delete_uni():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM University")
        result = cur.fetchall()
        return render_template("delete_uni.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM University")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM University WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_uni'))




@app.route('/Research_Center_add', methods = ['GET','POST'])
def insert_rc():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Research_Center")
        result = cur.fetchall()
        return render_template("insert_rc.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        budget = request.form["budget"]
        private_funds = request.form["private_funds"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Research_Center (id, budget, private_funds) VALUES (%s, %s, %s)", (id, budget, private_funds))
        con.commit()
        return redirect(url_for('insert_rc'))


@app.route('/Research_Center_edit', methods = ['GET','POST'])
def update_rc():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Research_Center")
        result = cur.fetchall()
        return render_template("update_rc.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        budget = request.form["budget"]
        private_funds = request.form["private_funds"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE Research_Center SET budget = %s, private_funds = %s WHERE id = %s", (budget, private_funds, id))
        con.commit()
        return redirect(url_for('update_rc'))


@app.route('/Research_Center_del', methods = ['GET','POST'])
def delete_rc():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Research_Center")
        result = cur.fetchall()
        return render_template("delete_rc.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Research_Center")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Research_Center WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_rc'))




@app.route('/Researcher_add', methods = ['GET','POST'])
def insert_res():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Researcher")
        result = cur.fetchall()
        return render_template("insert_res.html",result = result)
    if request.method == 'POST':
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        date_of_birth = request.form["date_of_birth"]
        gender = request.form["gender"]
        org_id = request.form["org_id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Researcher (first_name, last_name, date_of_birth, gender, org_id) VALUES (%s, %s, %s, %s, %s)", (first_name, last_name, date_of_birth, gender, org_id))
        con.commit()
        return redirect(url_for('insert_res'))


@app.route('/Researcher_edit', methods = ['GET','POST'])
def update_res():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Researcher")
        result = cur.fetchall()
        return render_template("update_res.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        date_of_birth = request.form["date_of_birth"]
        gender = request.form["gender"]
        org_id = request.form["org_id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE  Researcher SET first_name = %s, last_name = %s, date_of_birth = %s, gender = %s, org_id = %s WHERE id = %s", (first_name, last_name, date_of_birth, gender, org_id, id))
        con.commit()
        return redirect(url_for('update_res'))


@app.route('/Researcher_del', methods = ['GET','POST'])
def delete_res():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Researcher")
        result = cur.fetchall()
        return render_template("delete_res.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Researcher")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Researcher WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_res'))





@app.route('/Evaluation_add', methods = ['GET','POST'])
def insert_eva():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Evaluation")
        result = cur.fetchall()
        return render_template("insert_eva.html",result = result)
    if request.method == 'POST':
        grade = request.form["grade"]
        ev_date = request.form["ev_date"]
        researcher_id = request.form["researcher_id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Evaluation (grade, ev_date, researcher_id) VALUES (%s, %s, %s)", (grade, ev_date, researcher_id))
        con.commit()
        return redirect(url_for('insert_eva'))


@app.route('/Evaluation_edit', methods = ['GET','POST'])
def update_eva():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Evaluation")
        result = cur.fetchall()
        return render_template("update_eva.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        grade = request.form["grade"]
        ev_date = request.form["ev_date"]
        researcher_id = request.form["researcher_id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE  Evaluation SET grade = %s, ev_date = %s, researcher_id = %s WHERE id = %s", (grade, ev_date, researcher_id, id))
        con.commit()
        return redirect(url_for('update_eva'))


@app.route('/Evaluation_del', methods = ['GET','POST'])
def delete_eva():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Evaluation")
        result = cur.fetchall()
        return render_template("delete_eva.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Evaluation")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Evaluation WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_eva'))





@app.route('/Project_add', methods = ['GET','POST'])
def insert_proj():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Project")
        result = cur.fetchall()
        return render_template("insert_proj.html",result = result)
    if request.method == 'POST':
        title = request.form["title"]
        summary = request.form["summary"]
        date_start = request.form["date_start"]
        date_end = request.form["date_end"]
        amount = request.form["amount"]
        organisation_id = request.form["organisation_id"]
        program_id = request.form["program_id"]
        executive_id = request.form["executive_id"]        
        evaluation_id = request.form["evaluation_id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Project (title, summary, date_start, date_end, amount, organisation_id, program_id, executive_id, evaluation_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (title, summary, date_start, date_end, amount, organisation_id, program_id, executive_id, evaluation_id))
        con.commit()
        return redirect(url_for('insert_proj'))


@app.route('/Project_edit', methods = ['GET','POST'])
def update_proj():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Project")
        result = cur.fetchall()
        return render_template("update_proj.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        title = request.form["title"]
        summary = request.form["summary"]
        date_start = request.form["date_start"]
        date_end = request.form["date_end"]
        amount = request.form["amount"]
        organisation_id = request.form["organisation_id"]
        program_id = request.form["program_id"]
        executive_id = request.form["executive_id"]
        evaluation_id = request.form["evaluation_id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE  Project SET title = %s, summary = %s, date_start = %s, date_end = %s, amount = %s, organisation_id = %s, program_id = %s, executive_id = %s, evaluation_id = %s WHERE id = %s", (title, summary, date_start, date_end, amount, organisation_id, program_id, executive_id, evaluation_id, id))
        con.commit()
        return redirect(url_for('update_proj'))


@app.route('/Project_del', methods = ['GET','POST'])
def delete_proj():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Project")
        result = cur.fetchall()
        return render_template("delete_proj.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Project")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Project WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_proj'))




@app.route('/Scientific_Field_add', methods = ['GET','POST'])
def insert_sf():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Scientific_Field")
        result = cur.fetchall()
        return render_template("insert_sf.html",result = result)
    if request.method == 'POST':
        sf_name = request.form["sf_name"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Scientific_Field (sf_name) VALUES (%s)", (sf_name,))
        con.commit()
        return redirect(url_for('insert_sf'))



@app.route('/Scientific_Field_edit', methods = ['GET','POST'])
def update_sf():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Scientific_Field")
        result = cur.fetchall()
        return render_template("update_sf.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        sf_name = request.form["sf_name"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE Scientific_Field SET sf_name = %s WHERE id = %s", (sf_name, id))
        con.commit()
        return redirect(url_for('update_sf'))


@app.route('/Scientific_Field_del', methods = ['GET','POST'])
def delete_sf():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Scientific_Field")
        result = cur.fetchall()
        return render_template("delete_sf.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Scientific_Field")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Scientific_Field WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_sf'))



@app.route('/Deliverable_add', methods = ['GET','POST'])
def insert_del():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Deliverable")
        result = cur.fetchall()
        return render_template("insert_del.html",result = result)
    if request.method == 'POST':
        project_id = request.form["project_id"]
        title = request.form["title"]
        summary = request.form["summary"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("INSERT INTO Deliverable (project_id, title, summary) VALUES (%s, %s, %s)", (project_id, title, summary))
        con.commit()
        return redirect(url_for('insert_del'))


@app.route('/Deliverable_edit', methods = ['GET','POST'])
def update_del():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Deliverable")
        result = cur.fetchall()
        return render_template("update_del.html",result = result)
    if request.method == 'POST':
        id = request.form["id"]
        project_id = request.form["project_id"]
        title = request.form["title"]
        summary = request.form["summary"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("UPDATE  Deliverable SET project_id = %s, title = %s, summary = %s WHERE id = %s", (project_id, title, summary, id))
        con.commit()
        return redirect(url_for('update_del'))


@app.route('/Deliverable_del', methods = ['GET','POST'])
def delete_del():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Deliverable")
        result = cur.fetchall()
        return render_template("delete_del.html",result = result)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Deliverable")
        result = cur.fetchall()
        id = request.form["id"]
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("DELETE FROM Deliverable WHERE id = %s", (id,))
        con.commit()
        return redirect(url_for('delete_del'))



if __name__ == '__main__':
    app.run(debug=True)