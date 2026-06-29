import os
from flask import Flask, request, render_template
from flask_cors import CORS
import dotenv
from pymongo import MongoClient
from bson import ObjectId

# CONSTS
PAGE_SIZE = 12
# END CONSTS

dotenv.load_dotenv("./.env")

client = MongoClient(os.getenv("MONGO_CONN_STR"))
col = client["db_2026_06_02"]["map-stats"]

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["POST"])
def hello_world():
    sort_asc_desc = 1
    search_query = request.get_json()
    after = search_query.get("after", None)
    before = search_query.get("before", None)

    search_query.pop("after", None)
    search_query.pop("before", None)

    cursor = col.find(search_query).sort("_id", 1).limit(1)
    first = next(cursor, None)
    cursor = col.find(search_query).sort("_id", -1).limit(1)
    last = next(cursor, None)
    if first is None or last is None:
        return render_template("not_found.html")

    global_first_id = first["_id"]
    global_last_id = last["_id"]

    if before is not None and col.find_one({"_id": ObjectId(before)}) is not None and ObjectId(before) != ObjectId(global_first_id):
        search_query["_id"] = {"$lt": ObjectId(before)}
        sort_asc_desc = -1
    elif after is not None and col.find_one({"_id": ObjectId(after)}) is not None and ObjectId(after) != ObjectId(global_last_id):
        search_query["_id"] = {"$gt": ObjectId(after)}

    docs = col.find(search_query).sort(
        "_id", sort_asc_desc).limit(PAGE_SIZE)
    ldocs = list(docs)
    if sort_asc_desc == -1:
        ldocs = ldocs[::-1]
    return render_template("index.html", docs=ldocs, first_id=ldocs[0]["_id"], last_id=ldocs[-1]["_id"])


# if __name__ == "__main__":
#     app.run(debug=True)
