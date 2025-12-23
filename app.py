from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta, datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///apps.db" 
db = SQLAlchemy(app)

class Apps(db.Model):
    __tablename__ = "apps"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    amount = db.Column(db.Float,nullable=False)
    subtype = db.Column(db.String, nullable=False)
    subdate = db.Column(db.Date,nullable=False)
    expdate = db.Column(db.Date)
    subdays = db.Column(db.Integer)
    daysleft = db.Column(db.Integer)    

    def setdays(self):
        if self.expdate:
            self.subdays = (self.expdate-self.subdate).days
    
    def setexpdate(self):
        if self.subdays:
            self.expdate = self.subdate + timedelta(self.subdays)

    def setdaysleft(self):
        self.daysleft = (self.expdate - date.today()).days

    def __repr__(self):
        return f"{self.name},{self.subtype}"

    """ def renew(self):
        self.subdate = self.expdate
        self.setexpdate() """
        
with app.app_context():
    db.create_all()

@app.route('/',methods=['POST','GET'])
def index():    
    if request.method == 'POST':
        name = request.form["app"]
        amount = float(request.form["amount"])
        subtype = request.form["type"]
        subdate = datetime.strptime(request.form["subdate"],"%Y-%m-%d").date()
        expdate = request.form["expdate"]
        subdays = request.form["subdays"]
        if expdate:
            expdate = datetime.strptime(request.form["expdate"],"%Y-%m-%d").date()            
        if subdays:
            subdays = int(subdays)

        sub = Apps(
            name=name,
            amount=amount,
            subtype=subtype,
            subdate=subdate,
            expdate=expdate,
            subdays=subdays,
            )
        sub.setexpdate()
        sub.setdays()
        sub.setdaysleft()        

        db.session.add(sub)
        db.session.commit()        

    subs = db.session.query(Apps).all()    
    return render_template('index.html',subs=subs)

@app.route('/renew/<int:id>',methods=['POST','GET'])
def renew(id):
    sub = db.session.get(Apps,id)
    if request.method == 'POST':
       amount = float(request.form["amount"])
       subtype = request.form["type"]
       subdate = datetime.strptime(request.form["subdate"],"%Y-%m-%d").date()    
       expdate = request.form["expdate"]       
       subdays = request.form["subdays"]

       if expdate:
           expdate = datetime.strptime(request.form["expdate"],"%Y-%m-%d").date()
       if subdays:
           subdays = int(subdays)

       sub.amount = amount
       sub.subtype = subtype
       sub.subdate = subdate
       sub.expdate = expdate
       sub.subdays = subdays
       sub.setexpdate()
       sub.setdays()
       sub.setdaysleft()

       db.session.commit()

       return redirect(url_for('index'))
    
    return render_template('renew.html',sub=sub)

@app.route('/updat/<int:id>',methods=['POST','GET'])
def update(id):
    sub = db.session.get(Apps,id)
    if request.method == 'POST':
       name = request.form["app"]
       amount = float(request.form["amount"])
       subtype = request.form["type"]
       subdate = datetime.strptime(request.form["subdate"],"%Y-%m-%d").date()
       expdate = request.form["expdate"]
       subdays = request.form["subdays"]
       if expdate:
           expdate = datetime.strptime(request.form["expdate"],"%Y-%m-%d").date()        
       if subdays:
           subdays = int(subdays)

       sub.name = name
       sub.amount = amount
       sub.subtype = subtype
       sub.subdate = subdate
       sub.expdate = expdate
       sub.subdays = subdays
       sub.setexpdate()
       sub.setdays()
       sub.setdaysleft()

       db.session.commit()

       return redirect(url_for('index'))    

    return render_template('update.html',sub=sub)

@app.route('/delete/<int:id>')
def delete(id):
    sub = db.session.get(Apps,id)
    db.session.delete(sub)
    db.session.commit()

    return redirect(url_for('index'))