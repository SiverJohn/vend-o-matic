from flask import Blueprint, request, Response, json
import datafuncs as dataf

bp = Blueprint("root", __name__)


@bp.route("/", methods=["PUT", "DELETE"])
def coinManagement():
    if request.method == "PUT":
        inputJSON = request.get_json()
        (success, coins) = dataf.attempToInputCoin(inputJSON)
        if success:
            resp = Response(
                status="204",
                headers={"X-Coins": coins},
                mimetype="application/json",
            )
        else:
            resp = Response(
                response="ERROR 415: No Coins Inserted",
                status="415",
                mimetype="application/json",
            )
    elif request.method == "DELETE":
        coins = dataf.returnStoredCoins()
        resp = Response(
            status="204", headers={"X-Coins": coins}, mimetype="application/json"
        )
        return resp

    return resp


@bp.route("/inventory", methods=["GET"])
@bp.route("/inventory/<int:idx>", methods=["GET", "PUT"])
def inventoryManagement(idx=-1):
    if request.method == "GET":
        if idx >= 0:
            stock = dataf.getItemStock(idx)
            # stmt = sql.Select(Items).where(Items.id==idx)
            # item = db.session.execute(stmt).scalars().first()
            resp = Response(
                response=json.dumps(stock),
                status="200",
                mimetype="application/json",
            )
            return resp
        else:
            stocks = dataf.getInventoryStocks()
            resp = Response(
                response=json.dumps(stocks),
                status="200",
                mimetype="application/json",
            )
            return resp
    if request.method == "PUT":
        coins = dataf.currentUsableCoins()
        if idx >= 0:
            stock = dataf.getItemStock(idx)
        else:
            resp = Response(status="404", headers={"X-Coins": coins})
            return resp
        if stock > 0:
            if coins >= 2:
                stock -= 1
                coins = dataf.returnStoredCoins(2)
                dataf.updateItemStock(idx, stock)
                resp = Response(
                    response=json.dumps({"quantity": 1}),
                    status="200",
                    headers={
                        "X-Coins": coins,
                        "X-Inventory-Remaining": stock,
                    },
                    mimetype="application/json",
                )
            else:
                resp = Response(status="403", headers={"X-Coins": coins})
        else:
            resp = Response(status="404", headers={"X-Coins": coins})
        return resp
