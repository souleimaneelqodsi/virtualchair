from flask import request, g, current_app
from flask_restful import Resource
from flask_login import login_required, current_user
from datetime import datetime

from ..models.conference_model import ConferenceModel
from ..models.paper_model import PaperModel # For get_user_roles_for_conference


def format_date_or_none(date_obj):
    if isinstance(date_obj, datetime):
        return date_obj.date().isoformat()
    elif date_obj is not None and hasattr(date_obj, 'isoformat'): # Check if it's a date/datetime like object
        return date_obj.isoformat()
    return None


def format_datetime_or_none(datetime_obj):
    if datetime_obj:
        return datetime_obj.isoformat()
    return None


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
                    "start_date": format_date_or_none(conf.start_date),
                    "end_date": format_date_or_none(conf.end_date),
                    "location": conf.location,
                    "submission_deadline": format_datetime_or_none(
                        conf.submission_deadline
                    ),
                    "current_phase": conf.current_phase,
                    "created_at": format_datetime_or_none(conf.created_at),
                    "creator_id": str(conf.creator_id),
                }
                for conf in conferences
            ]
            return result, 200
        except ValueError as e:
            current_app.logger.error(f"ValueError in GET /conferences: {e}")
            return {"error": str(e)}, 400
        except Exception as e:
            current_app.logger.error(f"API error in GET /conferences: {e}", exc_info=True)
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
                creator_id=str(creator_id), # Ensure creator_id is string for model
            )

            return {
                "message": "Conférence créée avec succès.",
                "conference": {
                    "id": str(new_conference.id),
                    "name": new_conference.name,
                    "description": new_conference.description,
                    "start_date": format_date_or_none(new_conference.start_date),
                    "end_date": format_date_or_none(new_conference.end_date),
                    "location": new_conference.location,
                    "submission_deadline": format_datetime_or_none(
                        new_conference.submission_deadline
                    ),
                    "current_phase": new_conference.current_phase,
                    "created_at": format_datetime_or_none(new_conference.created_at),
                    "creator_id": str(new_conference.creator_id),
                },
            }, 201
        except ValueError as e:
            current_app.logger.error(f"ValueError in POST /conferences: {e}")
            return {"error": str(e)}, 400
        except Exception as e:
            current_app.logger.error(f"API error in POST /conferences: {e}", exc_info=True)
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
                "start_date": format_date_or_none(conference.start_date),
                "end_date": format_date_or_none(conference.end_date),
                "location": conference.location,
                "submission_deadline": format_datetime_or_none(
                    conference.submission_deadline
                ),
                "current_phase": conference.current_phase,
                "created_at": format_datetime_or_none(conference.created_at),
                "creator_id": str(conference.creator_id),
            }, 200
        except ValueError as e:
            current_app.logger.error(f"ValueError in GET /conferences/{conf_uuid}: {e}")
            return {"error": str(e)}, 400
        except Exception as e:
            current_app.logger.error(f"API error in GET /conferences/{conf_uuid}: {e}", exc_info=True)
            return {
                "error": "Erreur interne du serveur lors de la récupération de la conférence."
            }, 500

class ConferenceUserRolesResource(Resource):
    @login_required
    def get(self, conf_uuid: str):
        paper_model = PaperModel() # Contains get_user_roles_for_conference
        try:
            user_roles = paper_model.get_user_roles_for_conference(
                user_id=str(current_user.id),
                conference_id=conf_uuid
            )
            return {"roles": user_roles}, 200
        except Exception as e:
            current_app.logger.error(f"API error GET /conferences/{conf_uuid}/my-roles: {e}", exc_info=True)
            return {"error": "Erreur interne du serveur lors de la récupération des rôles."}, 500
