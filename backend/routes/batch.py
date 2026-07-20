from flask import Blueprint, jsonify

from services.s3_service import get_latest_batch_result
 
batch_bp = Blueprint("batch", __name__)
 
@batch_bp.route("/api/batch", methods=["GET"])

def batch():

    data = get_latest_batch_result()

    return jsonify(data)
 
