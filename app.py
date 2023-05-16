from flask import Flask, jsonify, request
from settings import connection, logger, handle_exceptions

app = Flask(__name__)


@app.route("/bank/insert", methods=["POST"])
@handle_exceptions
def create_account_id():
    # set the database connection
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection for creating a acoount_id")
    # information
    if "name" and "type"  not in request.json():
        raise Exception ("details missing")
    data = request.json
    name = data.get('name')
    type = data.get('type')
    balance = data.get('balance')
    if not name or not type or not balance:
        return "details are missing", 400
    cur.execute('INSERT INTO accountdetails(name,type,balance)'
                'VALUES (%s, %s, %s);',
                (name, type, balance))
    conn.commit()
    logger(__name__).warning("close the database connection as account_id is created")
    return jsonify("account created successfully")


# get account details of a particular account_id


@app.route("/bank/<int:account_id>", methods=["GET"], endpoint="get_account_information")
@handle_exceptions
def get_account_information(account_id):
    # set the database connection
    cur, conn = connection()
    logger(__name__).warning("starting the database connection for getting the information about account_id")
    cur.execute("SELECT name, type, balance FROM accountdetails WHERE account_id = %s", (account_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"message": "Account ID not found"})

    name, account_type, balance = row
    data = {
        "name": name,
        "type": account_type,
        "balance": balance
    }
    return jsonify({"message": "report of account_id", "details": data}), 200


@app.route("/bank/accounts", methods=["GET"], endpoint="get_all_account_information")
@handle_exceptions
def get_all_account_information():
    # set the database connection
    cur, conn = connection()
    logger(__name__).warning("starting the database connection for getting the information about account_id")

    cur.execute("SELECT name, type, balance,account_id FROM accountdetails ")
    rows = cur.fetchall()
    if not rows:
        return jsonify({"message": "Account ID not found"})
    data_list = []
    for row in rows:
        account_id, name, account_type, balance = row
        data = {
            "account_id" : account_id,
            "name": name,
            "type": account_type,
            "balance": balance
         }
        data_list.append(data)
    return jsonify({"message": "report of  all account_id", "details": data_list}), 200


# withdraw
@app.route("/withdraw", methods=["PUT"], endpoint="withdrawal")
@handle_exceptions
def withdrawal():
    # set the database connection
    cur, conn = connection()
    logger(__name__).warning("setting the database connection for withdrawing")
    if "account_id"and "amount" not in request.json():
        raise Exception ("details missing")
    account_id = request.json.get("account_id")
    amount = request.json.get("amount")
    cur.execute("SELECT balance FROM accountdetails WHERE account_id = %s", (account_id,))
    result = cur.fetchone()
    if not result:
        return "Account not found", 404
    balance = result[0]
    if int(balance) < int(amount):
        return "Insufficient balance", 400
    updated_amt = int(balance) - int(amount)
    cur.execute("""UPDATE accountdetails SET balance = %s  WHERE account_id = %s   """, (updated_amt, account_id))
    conn.commit()
    response = {
        "withdraw_amount": amount,
        "new_balance": updated_amt
    }
    return jsonify(response), 200


# deposit the amount
@app.route("/deposit", methods=["PUT"], endpoint="deposit_amount")
@handle_exceptions
def deposit_amount():
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection for updating the amount of a id")
    if "account_id" and "amount" not in request.json:
        raise Exception("details missing")
    account_id = request.json.get("account_id")
    amount = request.json.get("amount")

    cur.execute("SELECT balance FROM accountdetails WHERE account_id = %s", (account_id,))
    result = cur.fetchone()
    if not result:
        return "Account not found", 404
    balance = result[0]
    updated_amt = int(balance) + int(amount)
    cur.execute("""UPDATE accountdetails SET balance = %s  WHERE account_id = %s   """, (updated_amt, account_id))
    conn.commit()
    response = {
        "deposited_amount": amount,
        "new_balance": updated_amt
    }
    return jsonify(response), 200


# delete account_id
@app.route("/delete/<int:account_id>", methods=["DELETE"], endpoint="delete_account")
@handle_exceptions
def delete_account(account_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute("SELECT * FROM accountdetails WHERE account_id = %s", (account_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"message": f"Account with ID {account_id} not found"})

    cur.execute("DELETE FROM accountdetails WHERE account_id = %s", (account_id,))
    conn.commit()
    return "Record deleted successfully"


# update the account type
@app.route("/account_type/<int:account_id>",methods=["PUT"], endpoint="account_type")
@handle_exceptions
def account_type(account_id):
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection for updating the amount of a id")
    if "type" not in request.json:
        raise Exception ("details missing")
    data = request.get_json()
    account_type = data.get('type')
    cur.execute("SELECT type FROM accountdetails WHERE account_id = %s", (account_id,))
    result = cur.fetchone()
    if not result:
        return "Account not found", 404
    cur.execute("""UPDATE accountdetails SET type = %s  WHERE account_id = %s   """, (account_type , account_id))
    conn.commit()

    return "updated successfully", 200


# calculate the taxes of balance
@app.route("/taxes/<int:account_id>", methods=["GET"], endpoint="taxes")
@handle_exceptions
def taxes(account_id):
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection for updating the amount of a id")

    cur.execute("SELECT type,balance FROM accountdetails WHERE account_id = %s", (account_id,))
    result = cur.fetchone()
    if not result:
        return "Account not found", 404
    type, balance = result
    if type == "savings":
        taxes = (balance*5)/100
    else:
        taxes = (balance*8)/100
    return jsonify({"taxes per month": taxes})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
