from flask import Flask, url_for, redirect, request, session, Response, json
import sqlalchemy as sql

from schema import *
from config import *
import devUtils as dev

#app is stored in schema
if __name__=='__main__':
    app.config["SQLALCHEMY_DATABASE_URI"] =  dev.createSQLAlcURL()
    db.init_app(app)

    with app.app_context():
        db.create_all()
        db.session.commit()
        stmt = sql.select(Cash)
        cash = db.session.execute(stmt).scalars().first()
        if cash is None:
            dev.initializeDB(db.session)
        #mp.set_start_method('spawn')


def buildThingy(df):
    import sys
    print(df,file=sys.stdout)
    return '<p>Hello World</p>'

@app.route('/test')
def wombat():
    return buildThingy(None)
@app.route('/',methods=["PUT","DELETE"])
def coinManagement():
    if request.method == 'PUT':
        jsin = request.get_json()
        if 'coin' in jsin.keys() and jsin['coin']>=1:
            coin = db.get_or_404(Cash,'quarter_usd')
            coin.number+=1
            resp = Response(status='204',headers={'X-Coins:':coin.number},mimetype='application/json')
            db.session.commit()
            return resp
        else:
            resp = Response(response="ERROR 415: No Coins Inserted",status='415',mimetype='application/json')
            return resp
    elif request.method == 'DELETE':
        coin = db.get_or_404(Cash,'quarter_usd')
        resp = Response(status='204',headers={'X-Coins:':coin.number},mimetype='application/json')
        coin.number=0
        db.session.commit()
        return resp

@app.route('/inventory',methods=["GET"])
@app.route('/inventory/<int:idx>',methods=["GET","PUT"])
def inventoryManagement(idx=-1):
    if request.method == "GET":
        if idx>=0:
            item = db.get_or_404(Items,idx)
            #stmt = sql.Select(Items).where(Items.id==idx)
            #item = db.session.execute(stmt).scalars().first()
            resp = Response(response=json.dumps(item.inventory),status='200',mimetype='application/json')
            return resp
        else:
            stmt = sql.Select(Items)
            items = db.session.execute(stmt).scalars()
            resp = Response(response=json.dumps([x.inventory for x in items]),status='200',mimetype='application/json')
            return resp
    if request.method == "PUT":
        item = db.get_or_404(Items,idx)
        coin = db.get_or_404(Cash,'quarter_usd')
        if item.inventory >0:
            if coin.number >= 2:
                item.inventory-=1
                coin.number-=2
                resp = Response(status='200',headers={'X-Coins:':coin.number,'X-Inventory-Remaining:':item.inventory},mimetype='application/json')
                coin.number=0
                db.session.commit()
                return resp
            else:
                resp = Response(status='403',headers={'X-Coins:':coin.number})
                return resp
        else:
            resp = Response(status='404',headers={'X-Coins:':coin.number})
            return resp


if __name__ == '__main__':
    from waitress import serve
    print('Beginning Webserver')
    serve(app, host="0.0.0.0", port=3000, url_scheme="http")
    #serve(app, host="0.0.0.0", port=8080, url_scheme="https")
    #app.run()
