from flask import render_template, flash, redirect, request, session
from app import app
from dbconnect import connection

@app.route('/')
@app.route('/index')
def index():
    session.clear()
    session.clear()
    return render_template('index.html')

@app.route('/signup')
def disp():
    session.clear()
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    fname = request.form['inputFName']
    lname = request.form['inputLName']
    age= request.form['inputAge']
    mno= request.form['inputMobile']
    gender= request.form['inputGender']
    email= request.form['inputEmail']
    uname= request.form['inputUser']
    password = request.form['inputPassword']
    cur, conn = connection()
    y= cur.execute("SELECT * from Person where Person_id=%s",(uname))
    if int(y)>0:
    	err="Error: Username already exists!"
    	return render_template('signup.html', err=err)
    x= cur.execute("INSERT into Person(Person_id, Fname, Lname, Age, Mobile_no, email_id, Gender, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (uname, fname, lname, age, mno, email, gender, password))
    conn.commit()
    cur.close()
    conn.close()
    str="Registration Successful!"
    return render_template('index.html', msg=str)

@app.route('/login')
def screen():
    session.clear()
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    uname= request.form['inputUser']
    upass= request.form['inputPassword']
    session['uid']= uname
    session['pwd']=upass
    cur, conn= connection()
    x= cur.execute("SELECT password, Person_id, fname from Person WHERE Person_id=%s",(uname))
    if int(x)==0:
        err="Error: Username does not exist!"
        return render_template('login.html', err=err)
    y= cur.fetchone()
    session['user_name']=y[2]
    conn.commit()
    cur.close()
    conn.close()
    if upass==y[0]:
        return render_template('dashboard.html',name=y[2])
    else:
    	err="Error: Incorrect Username/Password!"
    	return render_template('login.html', err=err)

@app.route('/dashboard')
def dash():
	if session.get('uid'):
		uname=session.get('user_name',None)
		return render_template('dashboard.html', name=uname)
	else:
		return render_template('login.html')
#enquiry when two end points are given
@app.route('/enqj')
def enq():
	if session.get('uid'):
		return render_template('enqj.html')
	else:
		return render_template('login.html')
@app.route('/enqj', methods=['POST'])
def results():
    cur, conn= connection()
    start=request.form['inputStart']
    end=request.form['inputEnd']
    cur.execute("SELECT Train.Tnumber, Name from Train, Platform, Train_route where Platform.Platform_name=%s and Train_route.Tnumber=Train.Tnumber and Train_route.Platform_id=Platform.Platform_id",(start))
    starts=cur.fetchall()
    cur.execute("SELECT Train.Tnumber, Name from Train, Platform, Train_route where Platform.Platform_name=%s and Train_route.Tnumber=Train.Tnumber and Train_route.Platform_id=Platform.Platform_id",(end))
    ends=cur.fetchall()
    reqd= list(set(starts).intersection(ends))
    arrv=[]
    deps=[]
    for train in reqd:
    	cur.execute("SELECT exp_arrival from Train_route,Platform where Train_route.Platform_id=Platform.Platform_id and Tnumber=%s and Platform_name=%s",(train[0],start))
        ar=cur.fetchone()
        arrv.append(ar[0])
        cur.execute("SELECT exp_arrival from Train_route,Platform where Train_route.Platform_id=Platform.Platform_id and Tnumber=%s and Platform_name=%s",(train[0],end))
        dp=cur.fetchone()
        deps.append(dp[0])
    length=len(reqd)
    conn.commit()
    cur.close()
    conn.close()
    uid =session.get('uid',None)
    pwd=session.get('pwd',None)
    return render_template('enqj.html', trains=reqd, start=start, end=end, deps=deps, arrv=arrv, l=length)

@app.route('/enqt')
def enqt():
	if session.get('uid'):
		return render_template('enqt.html')
	else:
		return render_template('login.html')

@app.route('/enqt', methods=['POST'])
def trains():
    cur, conn = connection()
    tname= request.form['inputTname']
    cur.execute("SELECT Train.Name, Platform.Platform_Name, exp_arrival, exp_departure from Train_route, Train, Platform WHERE Train.Name=%s and Train.Tnumber=Train_route.Tnumber and Train_route.Platform_id=Platform.Platform_id ORDER BY Train_route.order_no", (tname))
    route=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('enqt.html', routes=route)

@app.route('/test')
def test():
    return render_template('test.html')
@app.route('/test', methods=['POST'])
def checkval():
    val=request.form['submit']
    print val
    return render_template('test.html')

@app.route('/booking')
def journey():
	if session.get('uid'):
		return render_template('booking.html')
	else:
		return render_template('login.html')

@app.route('/booking', methods=['POST'])
def book():
    cur, conn = connection()
    start=request.form['inputStart']
    end=request.form['inputEnd']
    seats=int(request.form['inputSeats'])
    doj=request.form['inputDate']
    cur.execute("Select Platform_id from Platform where Platform_name=%s", (start))
    x=cur.fetchone()[0]
    session['start_pt']=x
    cur.execute("Select Platform_id from Platform where Platform_name=%s", (end))
    y=cur.fetchone()[0]
    session['end_pt']=y
    session['seats']=seats
    session['date']=doj
    cur.execute("SELECT Train.Tnumber, Name from Train, Platform, Train_route where Platform.Platform_name=%s and Train_route.Tnumber=Train.Tnumber and Train_route.Platform_id=Platform.Platform_id",(start))
    a=cur.fetchall()
    cur.execute("SELECT Train.Tnumber, Name from Train, Platform, Train_route where Platform.Platform_name=%s and Train_route.Tnumber=Train.Tnumber and Train_route.Platform_id=Platform.Platform_id",(end))
    b=cur.fetchall()
    reqd= list(set(a).intersection(b))
    final=[]
    arrv=[]
    deps=[]
    cost=[]
    for train in reqd:
        c=cur.execute("SELECT * from Availability where Tnumber=%s and Date_of_Journey=%s", (train[0], doj))
        if int(c)>0:
            cur.execute("SELECT order_no from Train_route,Platform WHERE Train_route.Tnumber=%s and Platform.Platform_name=%s and Train_route.Platform_id=Platform.Platform_id", (train[0], start))
            ostart=cur.fetchone()[0]
            cur.execute("SELECT order_no from Train_route,Platform WHERE Train_route.Tnumber=%s and Platform.Platform_name=%s and Train_route.Platform_id=Platform.Platform_id", (train[0], end))
            oend=cur.fetchone()[0]
            if oend<ostart:
                oend, ostart = ostart, oend
            cur.execute("SELECT Seats_Available from Availability,Train_route WHERE Availability.Tnumber=Train_route.Tnumber and Availability.Tnumber=%s and order_no BETWEEN %s and %s", (train[0], ostart, oend))
            path=cur.fetchall()
            possible=True
            for pform in path:
                if (pform[0]<seats):
                    possible=False
                    break
            if possible==True:
                final.append(train)
        else:
            cur.execute("SELECT Platform_id from Train_route WHERE Tnumber=%s", (train[0]))
            ids=cur.fetchall()
            for pid in ids:
                cur.execute("INSERT into Availability(Tnumber, Platform_id, Date_of_Journey, Seats_Available) VALUES (%s,%s,%s,500)", (train[0], pid[0], doj))
            final.append(train)
    	cur.execute("Select * from Pricing where Tnumber=%s",(train[0]))
    	pr=cur.fetchone()
    	cur.execute("Select dist_x, dist_y from Platform where Platform_id=%s",(x))
    	p1=cur.fetchone()
        cur.execute("Select dist_x, dist_y from Platform where Platform_id=%s",(y))
        p2=cur.fetchone()
        dx= p2[0]-p1[0]
        dy= p2[1]-p1[1]
        dx=pow(dx,2)
        dy=pow(dy,2)
        dx=dx+dy
        cost_of_train=int(pow(dx,0.5))
        cost_of_train=pr[1]+(cost_of_train*pr[2])
        cost_of_train=cost_of_train*seats;
        cost.append(cost_of_train)
        cur.execute("SELECT exp_arrival from Train_route where Tnumber=%s and Platform_id=%s",(train[0],x))
        ar=cur.fetchone()
        arrv.append(ar)
        cur.execute("SELECT exp_arrival from Train_route where Tnumber=%s and Platform_id=%s",(train[0],y))
        dp=cur.fetchone()
        deps.append(dp)
   	conn.commit()
    cur.close()
    conn.close()
    session['final']=final
    session['costs']=cost
    l=len(final)
    return render_template('booktrain.html', final=final, length=l, costs=cost, starts=start, ends=end, doj=doj, arrv=arrv, deps=deps)

@app.route('/booktrain')
def options():
	if session.get('uid'):
		return render_template('booktrain.html')
	else:
		return render_template('login.html')

@app.route('/booktrain', methods=['POST'])
def ticket():
    final=session.get('final',None)
    ind=int(request.form['submit'])
    sid=session.get('start_pt',None)
    eid=session.get('end_pt',None)
    uname=session.get('uid',None)
    date=session.get('date',None)
    seats=session.get('seats',None)
    cur, conn= connection()
    x=cur.execute("SELECT PNR from Ticket ORDER by PNR desc")
    if int(x)==0:
        pnr=1738227265
    else:
        pnr=cur.fetchone()[0]+1
    costs=session.get('costs', None)
    cur.execute("INSERT into Ticket values(%s, %s, %s, %s, %s, %s, %s, %s)", (pnr, uname, final[ind][0], date, sid, eid, costs[ind], seats))
    cur.execute("SELECT order_no from Train_route where Tnumber=%s and Platform_id=%s",(final[ind][0], sid))
    ostart=cur.fetchone()[0]
    cur.execute("SELECT order_no from Train_route where Tnumber=%s and Platform_id=%s",(final[ind][0], eid))
    oend=cur.fetchone()[0]
    if oend<ostart:
        oend,ostart=ostart,oend
    cur.execute("SELECT Platform_id from Train_route where Tnumber=%s and order_no BETWEEN %s and %s",(final[ind][0],ostart,oend))
    pforms=cur.fetchall()
    for pform in pforms:
        cur.execute("UPDATE Availability set Seats_Available=Seats_Available-%s where Tnumber=%s and Platform_id=%s",(seats,final[ind][0],pform[0]))
    conn.commit()
    cur.close()
    conn.close()
    user_name=session.get('user_name',None)
    session.clear()
    session['uid']=uname
    session['user_name']=user_name
    return render_template('dashboard.html', name=user_name, msg="Booking Done!")

@app.route('/cancel')
def look():
    uid=session.get('uid',None)
    if uid:
    	cur,conn = connection()
    	cur.execute("SELECT * from Ticket where Person_ID=%s",(uid))
    	tickets=cur.fetchall()
    	length=len(tickets)
    	startp=[]
    	endp=[]
    	for ticket in tickets:
    		cur.execute("SELECT Platform_Name from Platform where Platform_id=%s",(ticket[4]))
    		pform=cur.fetchone()[0]
    		startp.append(pform)
    		cur.execute("SELECT Platform_Name from Platform where Platform_id=%s",(ticket[5]))
    		pform=cur.fetchone()[0]
    		endp.append(pform)
    	conn.commit()
    	cur.close()
    	conn.close()
    	return render_template('cancel.html', tickets=tickets, length=length, startp=startp, endp=endp)
    else:
    	return render_template('login.html')
@app.route('/cancel', methods=['POST'])
def cancel():
    uid=session.get('uid',None)
    cur,conn = connection()
    cur.execute("SELECT * from Ticket where Person_ID=%s",(uid))
    tickets=cur.fetchall()
    ind=int(request.form['submit'])
#PNR will be the first item in the tuple
    pnr=tickets[ind][0]
    sid=tickets[ind][4]
    lid=tickets[ind][5]
    doj=tickets[ind][3]
    tnum=tickets[ind][2]
    cur,conn = connection()
    seats=tickets[ind][7]
    cur.execute("SELECT order_no from Train_route WHERE Tnumber=%s and Platform_id=%s", (tnum, sid))
    ostart=cur.fetchone()[0]
    cur.execute("SELECT order_no from Train_route WHERE Tnumber=%s and Platform_id=%s", (tnum, lid))
    oend=cur.fetchone()[0]
    if oend<ostart:
        oend, ostart = ostart, oend
    cur.execute("SELECT Platform_id from Train_route where Tnumber=%s and order_no BETWEEN %s and %s",(tnum,ostart,oend))
    pforms=cur.fetchall()
    for pform in pforms:
        cur.execute("UPDATE Availability set Seats_Available=Seats_Available+%s where Tnumber=%s and Platform_id=%s",(seats,tnum,pform[0]))
    cur.execute("DELETE from Ticket where PNR=%s",(pnr))
    conn.commit()
    cur.close()
    conn.close()
    msg="Cancellation Done!"
    return render_template('dashboard.html', msg=msg, name=session.get('user_name',None))


@app.route('/history')
def history():
    uid=session.get('uid',None)
    if uid:
    	cur,conn = connection()
    	cur.execute("SELECT PNR, Train.Name, DOJ, Ticket.Start_ID, Ticket.Last_ID, Seats, Cost, Ticket.Tnumber from Ticket, Train where Train.Tnumber=Ticket.Tnumber and Person_ID=%s",(uid))
    	tickets=cur.fetchall()
    	sp=[]
    	ep=[]
    	arrv=[]
    	deps=[]
    	for ticket in tickets:
    		cur.execute("Select Platform_Name from Platform where Platform_id=%s",(ticket[3]))
    		st=cur.fetchone()
    		sp.append(st[0])
        	cur.execute("Select Platform_Name from Platform where Platform_id=%s",(ticket[4]))
    		end=cur.fetchone()
    		ep.append(end[0])
    		cur.execute("SELECT exp_arrival from Train_route where Tnumber=%s and Platform_id=%s",(ticket[7],ticket[3]))
        	ar=cur.fetchone()
        	arrv.append(ar)
        	cur.execute("SELECT exp_arrival from Train_route where Tnumber=%s and Platform_id=%s",(ticket[7],ticket[4]))
        	dp=cur.fetchone()
        	deps.append(dp)
       	conn.commit()
    	cur.close()
    	conn.close()
    	length=len(tickets)
    	return render_template('history.html', tickets=tickets, sp=sp, ep=ep, l=length, deps=deps, arrv=arrv)
    else:
    	return render_template('login.html')

