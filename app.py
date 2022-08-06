##############################################
##                                          ##
## Título: API MHealth4T2D                  ##
##                                          ##
##############################################
##                                          ##
## Descrição: API para a aplicação móvel    ##
## MHealth4T2D desenvolvida no âmbito da    ##
## cadeira de Projeto Integrado do CTESP    ##
## de TPSI                                  ##
##                                          ##
##############################################
##                                          ##
## Autor: Nuno Lopes                        ##
##                                          ##
##############################################
##                                          ##
## Data: 17/11/2021                         ##
##                                          ##
##############################################


from urllib import response
from flask import Flask, request
import mysql.connector
import json
import bcrypt
import time
from datetime import date, datetime

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

DB_HOST = "eu-cdbr-west-01.cleardb.com"
DB_USERNAME = "baa0fba5c9bfe1"
DB_PASSWORD = "33b4b636"
DB_NAME = "heroku_c8e571ca650980b"

NOT_FOUND_CODE = 404
OK_CODE = 200
SUCCESS_CODE = 201
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
FORBIDDEN_CODE = 403
SERVER_ERROR = 500

##########################################################
## Database Access                                      ##
##########################################################
def db_connection(host, database, username, pwd):
    
    db = mysql.connector.connect(
    host = host,
    database = database,
    user = username,
    password = pwd
    )

    return db

##########################################################
## Select on Database                                   ##
##########################################################
def db_select(host, database, username, pwd, query, args, mode):

    try:
        
        conn = db_connection(host, database, username, pwd)

        cursor = conn.cursor()

        cursor.execute(query, args)

        if mode == "fetchone":

            return cursor.fetchone()

        else:

            return cursor.fetchall()


    except (mysql.connector.Error) as exception:

        print(exception)
        return {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}

    finally:

        conn.close()

##########################################################
## Insert, Update or Delete on Database                 ##
##########################################################
def db_in_up_de(host, database, username, pwd, query, args):

    try:
        
        conn = db_connection(host, database, username, pwd)

        cursor = conn.cursor()

        cursor.execute(query, args)

        conn.commit()

        return cursor.rowcount

    except (mysql.connector.Error) as exception:

        print(exception)
        return False

    finally:

        conn.close()

##########################################################
## Get User ID                                          ##
##########################################################

def getUserId(email, password):

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT user_id, user_password FROM users WHERE user_email = %s", (email, ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return None

    if result == None or not result[0]:
        return None

    if not bcrypt.checkpw(password.encode("utf8"), bytes(result[1])):
        return None

    return result[0]

##########################################################
## Default Endpoint                                     ##
##########################################################
@app.route("/", methods=["GET"])
def hello_world():

    return json.dumps({"code": OK_CODE, "message": "Sucesso", "data": "Bem vindo à API Oficial do MHealth4T2D"}, ensure_ascii=False)

##########################################################
## Endpoint para o login                                ##
##########################################################
@app.route("/login/", methods=['POST'])
def login():

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request:
        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT user_password FROM users WHERE user_email = %s", (body_request["email"], ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result == None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Utilizador não encontrado.'}, ensure_ascii=False)

    if not bcrypt.checkpw(body_request["password"].encode("utf8"), bytes(result[0])):
        return json.dumps({"code": UNAUTHORIZED_CODE, "message": "Credenciais inválidas"}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso"}, ensure_ascii=False)

##########################################################
## Endpoint para o registo                              ##
##########################################################
@app.route("/signup/", methods=['POST'])
def user_signup():

    body_request = request.get_json()

    if body_request is None or "name" not in body_request or "email" not in body_request or "password" not in body_request or "gender" not in body_request or "birthdate" not in body_request:
        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)


    result = result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT COUNT(*) FROM users WHERE user_email = %s;", (body_request["email"], ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is not None and result[0]:
        return json.dumps({'code': BAD_REQUEST_CODE, "message": 'Email já em uso.'}, ensure_ascii=False)

    result = db_in_up_de(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "INSERT INTO users (user_name, user_email, user_password, user_gender_id, user_birthdate, user_position_id) VALUES (%s, %s, %s, (SELECT gender_id FROM genders WHERE gender_description = %s), %s, (SELECT position_id FROM positions WHERE position_description = 'Utilizador' LIMIT 1));", (body_request["name"], body_request["email"], bcrypt.hashpw(body_request["password"].encode("utf8"), bcrypt.gensalt(12)), body_request["gender"], body_request["birthdate"]))

    if not result:
        return json.dumps({"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente.", "data": body_request}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso"}, ensure_ascii=False)

##########################################################
## Endpoint para obter generos                          ##
##########################################################
@app.route("/getGenders/", methods=['GET'])
def getGenders():

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT gender_description FROM genders", (), "fetchall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        json.dumps(result, ensure_ascii=False)

    if result == None or not result:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Nenhum género encontrado.'}, ensure_ascii=False)

    genders = []

    for row in result:
        genders.append(row[0])


    return json.dumps({"code": OK_CODE, "message": "Sucesso", "genders" : genders}, ensure_ascii=False)


##########################################################
## Endpoint para obter questionários                    ##
##########################################################
@app.route("/getQuizzes/", methods=['POST'])
def getQuizzes():

    body_request = request.get_json()

    if "email" not in body_request or "password" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    #Consulta de questionários únicos
    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT distinct quizzes.quiz_title  as \"Quiz\" FROM quizzes INNER JOIN quizfrequency ON quizfrequency.quiz_frequency_id = quizzes.quiz_frequency_id INNER JOIN quizquestions ON quizquestions.quiz_question_id not in (SELECT quizanswers.quiz_question_id FROM quizanswers WHERE quizanswers.quiz_answer_user_id = %s) WHERE quizfrequency.quiz_frequency_description = %s;", (getUserId(body_request["email"], body_request["password"]) ,"Unique"), "fetchall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    quizzes = []

    for row in result:

        questions = []

        result2 = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT quizquestions.quiz_question as \"Question\", questioncategories.question_category_description as \"Category\" FROM quizquestions INNER JOIN questioncategories ON questioncategories.question_category_id = quizquestions.question_category_id INNER JOIN quizzes ON quizzes.quiz_id = quizquestions.quiz_id WHERE quizzes.quiz_title = %s ORDER BY quizquestions.quiz_question, questioncategories.question_category_description;", (row[0], ), "fetchall")

        if result2 == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
            return json.dumps(result2, ensure_ascii=False)

        for row2 in result2:

            questions.append({"question": row2[0] , "category": row2[1]})

        quizzes.append({"title": row[0], "questions" : questions})

    #Consulta de questionários trimestrais
    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT distinct quizzes.quiz_title  as \"Quiz\" FROM quizzes INNER JOIN quizfrequency ON quizfrequency.quiz_frequency_id = quizzes.quiz_frequency_id INNER JOIN quizquestions ON quizquestions.quiz_question_id not in (SELECT quizanswers.quiz_question_id FROM quizanswers WHERE quizanswers.quiz_answer_user_id = %s and TIMESTAMPDIFF(MONTH, quizanswers.quiz_answer_datetime, %s) >= 3) WHERE quizfrequency.quiz_frequency_description = %s;", (getUserId(body_request["email"], body_request["password"]), body_request["date"] if "date" in body_request else date.today(), "Quarterly"), "fetchall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    for row in result:

        questions = []

        result2 = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT quizquestions.quiz_question as \"Question\", questioncategories.question_category_description as \"Category\" FROM quizquestions INNER JOIN questioncategories ON questioncategories.question_category_id = quizquestions.question_category_id INNER JOIN quizzes ON quizzes.quiz_id = quizquestions.quiz_id WHERE quizzes.quiz_title = %s ORDER BY quizquestions.quiz_question, questioncategories.question_category_description;", (row[0], ), "fetchall")

        if result2 == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
            return json.dumps(result2, ensure_ascii=False)

        for row2 in result2:

            questions.append({"question": row2[0] , "category": row2[1]})

        quizzes.append({"title": row[0], "questions" : questions})

    #Consulta de Questionários Diários
    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT distinct quizzes.quiz_title  as \"Quiz\" FROM quizzes INNER JOIN quizfrequency ON quizfrequency.quiz_frequency_id = quizzes.quiz_frequency_id INNER JOIN quizquestions ON quizquestions.quiz_question_id not in (SELECT quizanswers.quiz_question_id FROM quizanswers WHERE quizanswers.quiz_answer_user_id = %s and TIMESTAMPDIFF(DAY, quizanswers.quiz_answer_datetime, %s) >= 1) WHERE quizfrequency.quiz_frequency_description = %s;", (getUserId(body_request["email"], body_request["password"]), body_request["date"] if "date" in body_request else date.today(), "Daily"), "fetchall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    for row in result:

        questions = []

        result2 = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT quizquestions.quiz_question as \"Question\", questioncategories.question_category_description as \"Category\" FROM quizquestions INNER JOIN questioncategories ON questioncategories.question_category_id = quizquestions.question_category_id INNER JOIN quizzes ON quizzes.quiz_id = quizquestions.quiz_id WHERE quizzes.quiz_title = %s ORDER BY quizquestions.quiz_question, questioncategories.question_category_description;", (row[0], ), "fetchall")

        if result2 == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
            return json.dumps(result2, ensure_ascii=False)

        for row2 in result2:

            questions.append({"question": row2[0] , "category": row2[1]})

        quizzes.append({"title": row[0], "questions" : questions})

    response = {"code": 200, "message": "sucesso", "quizzes": quizzes}

    return json.dumps(response, ensure_ascii=False)  

##########################################################
## Endpoint para obter questionários                    ##
##########################################################
@app.route("/insertQuiz/", methods=['POST'])
def insertQuiz():

    body_request = request.get_json()

    if "email" not in body_request or "password" not in body_request or "answer" not in body_request or "question" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_in_up_de(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "INSERT INTO quizanswers (quiz_answer, quiz_answer_complement, quiz_answer_datetime, quiz_question_id, quiz_answer_user_id) VALUES (%s, %s, %s, (SELECT quiz_question_id FROM quizquestions WHERE quiz_question = %s), %s);", (body_request["answer"], body_request["complement"] if "complement" in body_request else None, datetime.utcnow(), body_request["question"], getUserId(body_request["email"], body_request["password"])))

    if not result:

        return json.dumps({"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}, ensure_ascii=False)

    return json.dumps({"code": 200, "message": "Sucesso"}, ensure_ascii=False)

##########################################################
## Endpoint para obter a permisssao                     ##
##########################################################
@app.route("/getPosition/", methods=['POST'])
def getPosition():

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)


    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT positions.position_description FROM positions INNER JOIN users ON users.user_position_id = positions.position_id WHERE users.user_id = %s;", (getUserId(body_request["email"], body_request["password"]), ), "fetchall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        json.dumps(result, ensure_ascii=False)

    if result == None or not result:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Utilizador não encontrado'}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso", "position" : result[0][0]}, ensure_ascii=False)

##########################################################
## Endpoint para obter categorias de exercícios         ##
##########################################################
@app.route("/getExerciseCategories/", methods=['GET'])
def getExerciseCategories():

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT exercise_category_id, exercise_category_description FROM exercisecategories;", (), "fetchall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        json.dumps(result, ensure_ascii=False)

    if result == None or not result:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Nenhuma categoria encontrada.'}, ensure_ascii=False)

    categories = []

    for row in result:
        categories.append({"id": row[0], "category": row[1]})


    return json.dumps({"code": OK_CODE, "message": "Sucesso", "categories" : categories}, ensure_ascii=False)

##########################################################
## Endpoint para inserir exercícios                     ##
##########################################################
@app.route("/insertExercises/", methods=['POST'])
def insertExercises():

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request  or "title" not in body_request  or "description" not in body_request  or "category_id" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT COUNT(*) FROM exercisecategories WHERE exercise_category_id = %s;", (body_request["category_id"], ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Categoria não encontrada.'}, ensure_ascii=False)


    result = db_in_up_de(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "INSERT INTO exercises (exercise_title, exercise_description, exercise_category_id, exercise_image_link, exercise_video_link, exercise_registered_user_id) VALUES (%s, %s, %s, %s, %s, %s);", (body_request["title"], body_request["description"], body_request["category_id"], (body_request["image_link"] if "image_link" in body_request else None), (body_request["video_link"] if "video_link" in body_request else None), getUserId(body_request["email"], body_request["password"])))

    if not result:
        json.dumps({"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso"}, ensure_ascii=False)

##########################################################
## Endpoint para obter todos os utilizadores            ##
##########################################################
@app.route("/getUsers/", methods=['POST'])
def getUsers():

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request:
        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT positions.position_description FROM positions INNER JOIN users ON users.user_position_id = positions.position_id WHERE users.user_id = %s", (getUserId(body_request["email"], body_request["password"]), ), "fetchone")

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Utilizador que fez a requisição não encontrado.'}, ensure_ascii=False)

    if result[0] != "Administrador":
        return json.dumps({"code": FORBIDDEN_CODE, "message": "Você não tem acesso a esta informação"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT user_id, user_name FROM users", (), "fetchall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Nenhum utilizador encontrado.'}, ensure_ascii=False)

    
    users = []

    for row in result:
        users.append({"id": row[0], "name": row[1]})

    return json.dumps({"code": OK_CODE, "message": "Sucesso", "users": users}, ensure_ascii=False)

##########################################################
## Endpoint para obter um utilizador                    ##
##########################################################
@app.route("/getUsers/<id>", methods=['POST'])
def getUser(id):

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request:
        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    currentId = getUserId(body_request["email"], body_request["password"])

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT positions.position_description FROM positions INNER JOIN users ON users.user_position_id = positions.position_id WHERE users.user_id = %s", (getUserId(body_request["email"], body_request["password"]), ), "fetchone")

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Utilizador que fez a requisição não encontrado.'}, ensure_ascii=False)

    if result[0] != "Administrador" and int(id) != currentId:
        return json.dumps({"code": FORBIDDEN_CODE, "message": "Você não tem acesso a esta informação"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT user_name, user_email, (SELECT gender_description FROM genders WHERE gender_id = user_gender_id),  user_birthdate, user_goal_steps, user_goal_kal, user_goal_sleep, (SELECT position_description FROM positions WHERE position_id = user_position_id)  FROM users WHERE user_id = %s", (id, ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Nenhum utilizador encontrado.'}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso", "user": {"name": result[0], "email": result[1], "gender": result[2], "birthdate": result[3].__str__(), "goal_steps": result[4], "goal_kal": result[5], "goal_sleep": result[6], "position": result[7]}}, ensure_ascii=False)


##########################################################
## Endpoint para obter todos exercicios                 ##
##########################################################
@app.route("/getExercises/", methods=['GET'])
def getExercises():

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT exercises.exercise_id, exercises.exercise_title, exercises.exercise_description, exercises.exercise_image_link, exercises.exercise_video_link, exercisecategories.exercise_category_description FROM exercises INNER JOIN exercisecategories ON exercisecategories.exercise_category_id = exercises.exercise_category_id;", (), "fetchall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Nenhum exercício encontrado.'}, ensure_ascii=False)

    exercises = []

    for row in result:

        exercises.append({"id": row[0], "title": row[1], "description": row[2], "image_link": row[3], "video_link": row[4], "category": row[5]})

    return json.dumps({"code": OK_CODE, "message": "Sucesso", "exercises": exercises}, ensure_ascii=False)

##########################################################
## Endpoint para associar um exercício                  ##
##########################################################
@app.route("/associateExercise/", methods=['POST'])
def associateExercise():

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request or "exercise_id" not in body_request or "datetime" not in body_request or "user_id" not in body_request:
        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT COUNT(*) FROM exerciseplan WHERE exercise_plan_datetime = %s and exercise_plan_exercise_id = %s and exercise_plan_aim_user_id = %s;", (body_request["datetime"], body_request["exercise_id"], body_request["user_id"]), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result and result[0] != 0:
        return json.dumps({'code': BAD_REQUEST_CODE, "message": 'Exercício já registado com essa data e com esse utilizador.'}, ensure_ascii=False)

    result = db_in_up_de(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "INSERT INTO exerciseplan (exercise_plan_datetime, exercise_plan_exercise_id, exercise_plan_register_user_id, exercise_plan_aim_user_id) VALUES (%s, %s, %s, %s);", (body_request["datetime"], body_request["exercise_id"], getUserId(body_request["email"], body_request["password"]), body_request["user_id"]))

    if not result:
        json.dumps({"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso"}, ensure_ascii=False)

##########################################################
## Endpoint para atualizar um exercício                 ##
##########################################################
@app.route("/updateExercise/<id>", methods=['POST'])
def updateExercise(id):

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request or "title" not in body_request  or "description" not in body_request  or "category_id" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT COUNT(*) FROM exercisecategories WHERE exercise_category_id = %s;", (body_request["category_id"], ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Categoria não encontrada.'}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT COUNT(*) FROM exercises WHERE exercise_id = %s;", (id, ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Exercício não encontrado.'}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT positions.position_description FROM positions INNER JOIN users ON users.user_position_id = positions.position_id WHERE users.user_id = %s", (getUserId(body_request["email"], body_request["password"]), ), "fetchone")

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Utilizador que fez a requisição não encontrado.'}, ensure_ascii=False)

    if result[0] != "Administrador":
        return json.dumps({"code": FORBIDDEN_CODE, "message": "Você não tem acesso a esta operação"}, ensure_ascii=False)

    result = db_in_up_de(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "UPDATE exercises SET exercise_title = %s, exercise_description = %s, exercise_image_link = %s, exercise_video_link  = %s, exercise_registered_user_id  = %s, exercise_category_id  = %s WHERE exercise_id = %s", (body_request["title"], body_request["description"], (body_request["image_link"] if "image_link" in body_request else None), (body_request["video_link"] if "video_link" in body_request else None), getUserId(body_request["email"], body_request["password"]), body_request["category_id"], id))

    if not result:
        json.dumps({"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso"}, ensure_ascii=False)

##########################################################
## Endpoint para eliminar um exercício                  ##
##########################################################
@app.route("/deleteExercise/<id>", methods=['POST'])
def deleteExercise(id):

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT COUNT(*) FROM exercises WHERE exercise_id = %s;", (id, ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Exercício não encontrado.'}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT positions.position_description FROM positions INNER JOIN users ON users.user_position_id = positions.position_id WHERE users.user_id = %s", (getUserId(body_request["email"], body_request["password"]), ), "fetchone")

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Utilizador que fez a requisição não encontrado.'}, ensure_ascii=False)

    if result[0] != "Administrador":
        return json.dumps({"code": FORBIDDEN_CODE, "message": "Você não tem acesso a esta operação"}, ensure_ascii=False)

    result = db_in_up_de(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "DELETE FROM exerciseplan WHERE exercise_plan_exercise_id = %s;", (id, ))

    if not result:
        json.dumps({"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}, ensure_ascii=False)

    result = db_in_up_de(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "DELETE FROM exercises WHERE exercise_id = %s;", (id, ))

    if not result:
        json.dumps({"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso"}, ensure_ascii=False)

##########################################################
## Endpoint para obter o plano de exercícios            ##
##########################################################
@app.route("/getPlan/", methods=['POST'])
def getPlan():

    body_request = request.get_json()

    if body_request is None or "email" not in body_request or "password" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT exercises.exercise_id, exercises.exercise_title, exercises.exercise_description, exercises.exercise_image_link, exercises.exercise_video_link, exercisecategories.exercise_category_description, exerciseplan.exercise_plan_datetime FROM exercises INNER JOIN exercisecategories ON exercisecategories.exercise_category_id = exercises.exercise_category_id INNER JOIN exerciseplan ON exerciseplan.exercise_plan_exercise_id = exercises.exercise_id WHERE exerciseplan.exercise_plan_aim_user_id = %s and exerciseplan.exercise_plan_datetime BETWEEN CONCAT(%s, ' 00:00:00') AND CONCAT(%s, ' 23:59:59');", (getUserId(body_request["email"], body_request["password"]), (body_request["date"] if "date" in body_request else datetime.today().strftime('%Y-%m-%d')), (body_request["date"] if "date" in body_request else datetime.today().strftime('%Y-%m-%d'))), "fecthall")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Plano não econtrado.'}, ensure_ascii=False)

    exercises = []

    for row in result:

        exercises.append({"id": row[0], "title": row[1], "description": row[2], "image_link": row[3], "video_link": row[4], "category": row[5], "datetime": row[6].__str__()})

    return json.dumps({"code": OK_CODE, "message": "Sucesso", "exercises": exercises}, ensure_ascii=False) 

    
##########################################################
## Endpoint para obter um exercicio                     ##
##########################################################
@app.route("/getExercises/<id>", methods=['GET'])
def getExercise(id):

    result = db_select(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "SELECT exercises.exercise_title, exercises.exercise_description, exercises.exercise_image_link, exercises.exercise_video_link, exercisecategories.exercise_category_description FROM exercises INNER JOIN exercisecategories ON exercisecategories.exercise_category_id = exercises.exercise_category_id WHERE exercises.exercise_id = %s;", (id, ), "fetchone")

    if result == {"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}:
        return json.dumps(result, ensure_ascii=False)

    if result is None or not result[0]:
        return json.dumps({'code': NOT_FOUND_CODE, "message": 'Nenhum exercício encontrado.'}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso", "exercise": {"title": result[0], "description": result[1], "image_link": result[2], "video_link": result[3], "category": result[4]}}, ensure_ascii=False)


##########################################################
## Endpoint para obter o perfil                         ##
##########################################################
@app.route("/getProfile/", methods=['POST'])
def getProfile():

    body_request = request.get_json()

    if "email" not in body_request or "password" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    return getUser(getUserId(body_request["email"], body_request["password"]))

##########################################################
## Endpoint para atualizar o perfil                     ##
##########################################################
@app.route("/editProfile/", methods=['POST'])
def editProfile():

    body_request = request.get_json()

    if "email" not in body_request or "password" not in body_request or "name" not in body_request or "gender" not in body_request or "birthdate" not in body_request or "steps_goal" not in body_request or "kal_goal" not in body_request or "sleep_goal" not in body_request:

        return json.dumps({"code": BAD_REQUEST_CODE, "message": "Parâmetros inválidos"}, ensure_ascii=False)

    result = db_in_up_de(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, "UPDATE users SET user_name = %s, user_gender_id = (SELECT gender_id FROM genders WHERE gender_description = %s LIMIT 1), user_birthdate = %s, user_goal_steps = %s, user_goal_kal = %s, user_goal_sleep = %s WHERE user_id = %s", (body_request["name"], body_request["gender"], body_request["birthdate"], body_request["steps_goal"], body_request["kal_goal"], body_request["sleep_goal"], getUserId(body_request["email"], body_request["password"])))

    if not result:

        json.dumps({"code": SERVER_ERROR, "message": "Um exceção foi gerada inesperadamente."}, ensure_ascii=False)

    return json.dumps({"code": OK_CODE, "message": "Sucesso"}, ensure_ascii=False)


##########################################################
## MAIN                                                 ##
##########################################################
if __name__ == "__main__":

    time.sleep(2)

    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)