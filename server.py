from crypt import methods
from flask import Flask, Response, render_template, request, flash
import requests, json
import sqlite3
import secrets

app=Flask(__name__)
app.secret_key=secrets.token_urlsafe(32)
conn=sqlite3.connect('autosource.db',check_same_thread=False, timeout=10000)
cursor=conn.cursor()

@app.route('/')
@app.route('/index', methods= ['GET', 'POST'])
def index():
  global brands,models,colors,titles,years
  brands = cursor.execute("select distinct brand from cars order by brand").fetchall()
  models = cursor.execute("select distinct model,brand from cars").fetchall()
  colors = cursor.execute("select distinct color from cars").fetchall()
  titles = cursor.execute("select distinct title_status from cars").fetchall()
  years = cursor.execute("select distinct year from cars order by year").fetchall()

  return render_template('index.html', brands=brands, models=models, titles=titles, colors=colors, years=years)

@app.route('/filter', methods=['POST'])
def filterData():
  queryList = list()
  joinStr = ' and '
  # if(request.form.get('brand')): queryString = queryString+ 'brand = '+request.form.get('brand')
  formDict = request.form.to_dict()
  app.logger.info(formDict)
  for x in formDict:
    if formDict[x]:
      if x !='startYear' and x !='endYear' and x !='maxCost' and x !='minCost':
       queryList.append(x+'='+'"'+formDict[x]+'"')
    else: 
     continue
      
  app.logger.info(queryList)
  builtQuery = joinStr.join(queryList)
  app.logger.info(builtQuery)

  result = cursor.execute('select c.*,d.name,i.path,d.dealer_id from cars c left join images i using(model) left join dealer d using(dealer_id) where '+builtQuery ).fetchall()
  
  return render_template('cars_list.html', result=result, length=len(result))


@app.route('/test_drive')
def testDrive():
  return render_template('test_drive.html')

@app.route('/submit', methods=['POST'])
def submit():
    name=request.form.get('name')
    phone=request.form.get('contact')
    email=request.form.get('email')
    cursor.execute('INSERT INTO customers(name,phone,email) VALUES(?,?,?)',(name,phone,email))
    conn.commit()
    # dealer = cursor.execute('select * from dealer').fetchall()
    # app.logger.info(dealer)
    return index()

@app.route('/dealer_info/<path:id>', methods=['GET'])
def dealer_info(id):

  
  dealerData = cursor.execute("select * from dealer where dealer_id=?",[id]).fetchall()
  app.logger.info(dealerData)
  return render_template('dealer_info.html', dealerData=dealerData)

@app.route('/home', methods=['POST'])
def home():
  return index()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
