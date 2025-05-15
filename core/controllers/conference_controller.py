from flask import request, g
from flask_restful import Resource
from flask_login import login_required, current_user
from datetime import datetime

from ..models.conference_model import ConferenceModel


class ConferenceListCreateResource(Resource):
    def get(self):
        conference_service = ConferenceModel()
        try:
            conferences = conference_service.get_all_conferences()

            result = [
                {
                    "id": str(conf.id),
                    "name": conf.name,
                    "description": conf.description,
                    "start_date": str(conf.start_date) if conf.start_date else None,
                    "end_date": str(conf.end_date) if conf.end_date else None,
                    "location": conf.location,
                    "submission_deadline": conf.submission_deadline.isoformat()
                    if conf.submission_deadline
                    else None,
                    "current_phase": conf.current_phase,
                    "created_at": conf.created_at.isoformat()
                    if conf.created_at
                    else None,
                    "creator_id": str(conf.creator_id),
                }
                for conf in conferences
            ]
            return result, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            print(f"API error in GET /conferences: {e}")
            return {
                "error": "Erreur interne du serveur lors de la récupération des conférences."
            }, 500

    @login_required
    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "Données JSON requises."}, 400

        name = data.get("name")
        description = data.get("description")
        start_date_str = data.get("start_date")
        end_date_str = data.get("end_date")
        location = data.get("location")
        submission_deadline_str = data.get("submission_deadline")
        current_phase = data.get("current_phase")

        if not name:
            return {"error": "Le champ 'name' est requis."}, 400

        creator_id = current_user.id

        conference_service = ConferenceModel()
        try:
            new_conference = conference_service.create_conference(
                name=name,
                description=description,
                start_date_str=start_date_str,
                end_date_str=end_date_str,
                location=location,
                submission_deadline_str=submission_deadline_str,
                current_phase=current_phase,
                creator_id=creator_id,
            )

            return {
                "message": "Conférence créée avec succès.",
                "conference": {
                    "id": str(new_conference.id),
                    "name": new_conference.name,
                    "description": new_conference.description,
                    "start_date": str(new_conference.start_date),
                    "end_date": str(new_conference.end_date),
                    "location": new_conference.location,
                    "submission_deadline": new_conference.submission_deadline.isoformat(),
                    "current_phase": new_conference.current_phase,
                    "created_at": new_conference.created_at.isoformat(),
                    "creator_id": str(new_conference.creator_id),
                },
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            print(f"API error in POST /conferences: {e}")
            return {
                "error": "Erreur interne du serveur lors de la création de la conférence."
            }, 500


class ConferenceDetailResource(Resource):
    def get(self, conf_uuid: str):
        conference_service = ConferenceModel()
        try:
            conference = conference_service.get_conference_by_id(conf_uuid)
            if not conference:
                return {"error": "Conférence introuvable."}, 404

            return {
                "id": str(conference.id),
                "name": conference.name,
                "description": conference.description,
                "start_date": str(conference.start_date)
                if conference.start_date
                else None,
                "end_date": str(conference.end_date) if conference.end_date else None,
                "location": conference.location,
                "submission_deadline": conference.submission_deadline.isoformat()
                if conference.submission_deadline
                else None,
                "current_phase": conference.current_phase,
                "created_at": conference.created_at.isoformat(),
                "creator_id": str(conference.creator_id),
            }, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            print(f"API error in GET /conferences/{conf_uuid}: {e}")
            return {
                "error": "Erreur interne du serveur lors de la récupération de la conférence."
            }, 500
