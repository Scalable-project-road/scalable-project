from flask import Blueprint, jsonify
 
from services.s3_service import get_latest_batch_result

from services.realtime_service import get_latest_realtime
 
comparison_bp = Blueprint("comparison", __name__)
 
 
@comparison_bp.route("/api/comparison", methods=["GET"])

def comparison():
 
    batch = get_latest_batch_result()
 
    realtime = get_latest_realtime()
 
    return jsonify({

        "batch": batch,

        "realtime": realtime

    })
 
