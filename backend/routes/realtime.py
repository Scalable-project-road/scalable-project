from flask import Blueprint, jsonify
from services.realtime_service import get_latest_realtime
 
realtime_bp = Blueprint("realtime", __name__)
 
 
@realtime_bp.route("/api/realtime", methods=["GET"])
def realtime():
 
    return jsonify(get_latest_realtime())
