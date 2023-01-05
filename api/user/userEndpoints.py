import pandas as pd
from flask import Flask, jsonify ,request,Response
import json
import mysql.connector as sql
import logging
from flask_cors import CORS
from flask_cors import cross_origin
from datetime import datetime
import re
import os
import base64
from random import randint
from kafka import KafkaProducer, producer
app=Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_ADMIN_USER = os.getenv("MYSQL_USER")
MYSQL_ADMIN_PASSWORD = os.getenv("MYSQL_PASSWORD")
MY_DB = os.getenv("PARENT_DB")
USER_FLASK_IPADDRESS = '0.0.0.0'
USER_FLASK_PORT = os.getenv("USER_FLASK_PORT")
KAFKA_HOST=os.getenv('KAFKA_HOST')
KAFKA_PORT=os.getenv('KAFKA_PORT')
ORDER_KAFKA_TOPIC = os.getenv('KAFKA_ORDERS_TOPIC')


@app.route('/user/createUser',methods=['post'])
@cross_origin()
def createUser():

    con = sql.connect(host=MYSQL_HOST,user=MYSQL_ADMIN_USER,password=MYSQL_ADMIN_PASSWORD,db=MY_DB, use_unicode=True, charset='utf8')
    cur = con.cursor()
    try:
        name=request.form.get('name')
    except:
        return jsonify({"Error":"Enter the Name of user"})
    try:
        emailId=request.form.get('emailId')
    except:
        return jsonify({"Error":"Enter the emailId"})
    try:
        password=request.form.get('password')
    except:
        return jsonify({"Error":"Enter the password"})
    try:
        phoneNumber=request.form.get('phoneNumber')
    except:
        return jsonify({"Error":"Enter the phoneNumber"})
    try:
    	cur.execute("SELECT emailId FROM users WHERE emailId='%s'"%format(emailId))
    	data = cur.fetchall()
    	user=pd.Series(data)
    	if(not user.empty >0):
    	   return jsonify({"Error": "User already has an account, try logging in!!"})
    except Exception as e:
        return jsonify({"Error":str(e)})
    try:
        cur.execute("INSERT INTO users (userName,emailId, phoneNumber, password) \
        	VALUES ('%s','%s','%s','%s') "%(name,emailId,phoneNumber,password))
        con.commit()
        return jsonify({"status":200})
    except Exception as e:
        print(e)
        return jsonify({"Error":str(e)})

@app.route('/user/loginUser',methods=['post'])
@cross_origin()
def loginUser():
    con = sql.connect(host=MYSQL_HOST,user=MYSQL_ADMIN_USER,password=MYSQL_ADMIN_PASSWORD,db=MY_DB, use_unicode=True, charset='utf8')
    cur = con.cursor()
    try:
        emailId=request.form.get('emailId')
    except:
        return jsonify({"Error":"Enter the emailId"})
    try:
        password=request.form.get('password')
    except Exception as e:
        print(e)
        return jsonify({"Error":str(e)})
    try:
        cur.execute("SELECT * FROM users WHERE emailId='%s' AND password='%s' "%(emailId,password))
        data = cur.fetchall()
        user=pd.Series(data)
        # print(user)
        if(not user.empty):
            userName = user[0][1]
            return jsonify({"status":200})
        else:
        	return jsonify({"Error":"username/password is wrong, create an account"})
    except Exception as e:
        print(str(e))
        return jsonify({"Error":str(e)})

@app.route('/user/listFoodItems',methods=['get'])
@cross_origin()
def listFoodItems():
    try:
        con = sql.connect(host=MYSQL_HOST,user=MYSQL_ADMIN_USER,password=MYSQL_ADMIN_PASSWORD,db=MY_DB, use_unicode=True, charset='utf8')
        cur = con.cursor()
        cur.execute("SELECT * FROM foodItems")
        data = cur.fetchall()
        test_df=pd.DataFrame(data)
        print(test_df)
        test_df.columns=['foodId','emailId','foodName','updated on', 'description', 'address', 'pincode', 'isVeg', 'isNutsFree', 'isGlutenFree', 'isDairyFree', 'quantity']
        # print("Kireti")
        test_json=test_df.to_json(orient='records')
        # print("kireeti - 2")
        resp=Response(response=test_json,status=200,mimetype="application/json")
        # print("kireeti -3")
        return resp
    except Exception as e:
        return jsonify({"Error":str(e)})


@app.route('/user/orderCartItems',methods=['post'])
@cross_origin()
def orderCartItems():
    try:
        itemCart=request.form.get('itemCart')
    except:
        return jsonify({"Error":"Enter the items"})
    try:
        emailId=request.form.get('emailId')
    except:
        return jsonify({"Error":"Enter the emailId"})
    try:
        con = sql.connect(host=MYSQL_HOST,user=MYSQL_ADMIN_USER,password=MYSQL_ADMIN_PASSWORD,db=MY_DB, use_unicode=True, charset='utf8')
        cur = con.cursor()
        items_dict = json.loads(itemCart)
        flag =0
        print("Type:", type(items_dict))
        print(items_dict)
        foodItemsList=[]
        for key in items_dict:
            print(key)
            cur.execute("SELECT * FROM foodItems WHERE foodId=%d"%(int(key)))
            data=cur.fetchall()
            quant=pd.Series(data)
            if(not quant.empty):
                currentQuantity = int(quant[0][11])
                print(currentQuantity)
                if currentQuantity == int(items_dict[key]):
                    cur.execute("DELETE FROM foodItems WHERE foodId='%s'"%(key))
                elif currentQuantity > int(items_dict[key]):
                    foodItemDict = {}
                    cur.execute("UPDATE foodItems SET quantity=%d WHERE foodId='%s'"%(currentQuantity-int(items_dict[key]),key))
                    # data[0][11]=items_dict[key]
                    foodItemDict["foodId"]=quant[0][0]
                    foodItemDict["donorEmailId"]=quant[0][1]
                    foodItemDict["foodName"]=quant[0][2]
                    foodItemDict["description"]=quant[0][4]
                    foodItemDict["address"]=quant[0][5]
                    foodItemDict["pincode"]=quant[0][6]
                    foodItemDict["isVeg"]=quant[0][7]
                    foodItemDict["isNutsFree"]=quant[0][8]
                    foodItemDict["isGlutenFree"]=quant[0][9]
                    foodItemDict["isDairyFree"]=quant[0][10]
                    foodItemDict["quantity"]=quant[0][11]
                    foodItemsList.append(foodItemDict)
                    logging.warning(foodItemDict)
                else:
                	return jsonify({"Error": "Not enough quantity for the item %s"%(quant[0][2])})
                con.commit()
            else:
            	return jsonify({"Error": "one of the items removed by the Donor, please check again!!"})
        cur.execute("SELECT * FROM users WHERE emailId='%s'"%(emailId))
        userDetails = cur.fetchall()
        uDetails =pd.Series(userDetails)
        userDetailsDict ={}
        userDetailsDict["userId"]=uDetails[0][0]
        userDetailsDict["userName"]=uDetails[0][1]
        userDetailsDict["userEmailId"]=uDetails[0][2]
        userDetailsDict["userPhoneNumber"]=uDetails[0][3]
        logging.warning(userDetailsDict)
        dictionary ={}
        # orderId = base64.b64encode(os.urandom(6)).decode('ascii')
        orderId = str(randint(10**9, 10**10 -1))
        dictionary['userDetails']=userDetailsDict
        dictionary['foodItems']=foodItemsList
        dictionary['orderTime']=datetime.now().strftime('%s')
        dictionary['orderId']=orderId
        logging.warning(dictionary)
        logging.warning("Came till prev orders statement")
       	for key in items_dict:
            cur.execute("INSERT INTO orders (orderId,userEmail, foodId, quantity) \
            	VALUES ('%s','%s','%s','%d') "%(orderId,emailId,key,int(items_dict[key])))
            logging.warning("inside key loop",key)
        con.commit()
        logging.warning("done inserting into orders")
        producer.send(ORDER_KAFKA_TOPIC,json.dumps(dictionary).encode("utf-8"))
        logging.warning("pushed to kafka")
        return jsonify({"status":200})
    except Exception as e:
        return jsonify({"Error":str(e)})


if __name__ == '__main__':
    btServer = KAFKA_HOST+":"+str(KAFKA_PORT)
    producer = KafkaProducer(bootstrap_servers=btServer)
    app.run(USER_FLASK_IPADDRESS,port=USER_FLASK_PORT,debug=True)
