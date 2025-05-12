from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.tables import Conference
from core.app import SessionLocal
from datetime import datetime
from core.tables import Paper, Evaluation, EvaluationRecommendationEnum


class ConferenceCreateResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        name = data.get("name")
        description = data.get("description")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        location = data.get("location")
        submission_deadline = data.get("submission_deadline")

        if not name:
            return {"message": "Le nom est requis"}, 400

        user = get_jwt_identity()
        session = SessionLocal()

        try:
            conference = Conference(
                name=name,
                description=description,
                start_date=datetime.strptime(start_date, "%Y-%m-%d") if start_date else None,
                end_date=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None,
                location=location,
                submission_deadline=datetime.strptime(submission_deadline, "%Y-%m-%d %H:%M:%S")
                    if submission_deadline else None,
                creator_id=user["id"]
            )
            session.add(conference)
            session.commit()
            return {"message": "Conférence créée avec succès", "id": str(conference.id)}, 201

        except Exception as e:
            session.rollback()
            return {"error": f"Erreur serveur : {str(e)}"}, 500

        finally:
            session.close()

class ConferenceListResource(Resource):
    def get(self):
        session = SessionLocal()
        try:
            conferences = session.query(Conference).all()
            result = []
            for conf in conferences:
                result.append({
                    "id": str(conf.id),
                    "name": conf.name,
                    "description": conf.description,
                    "start_date": str(conf.start_date) if conf.start_date else None,
                    "end_date": str(conf.end_date) if conf.end_date else None,
                    "location": conf.location,
                    "submission_deadline": str(conf.submission_deadline) if conf.submission_deadline else None,
                    "creator_id": str(conf.creator_id)
                })
            return jsonify(result)
        except Exception as e:
            session.rollback()
            return {"error": f"Erreur : {str(e)}"}, 500
        finally:
            session.close()

class ConferenceDetailResource(Resource):
    def get(self, conf_id):
        session = SessionLocal()
        try:
            conference = session.query(Conference).filter_by(id=conf_id).first()
            if not conference:
                return {"error": "Conférence introuvable"}, 404

            return {
                "id": str(conference.id),
                "name": conference.name,
                "description": conference.description,
                "start_date": str(conference.start_date) if conference.start_date else None,
                "end_date": str(conference.end_date) if conference.end_date else None,
                "location": conference.location,
                "submission_deadline": str(conference.submission_deadline) if conference.submission_deadline else None,
                "creator_id": str(conference.creator_id)
            }, 200

        except Exception as e:
            return {"error": f"Erreur serveur : {str(e)}"}, 500
        finally:
            session.close()


from core.tables import Conference, ConferenceRole, ConferenceRoleEnum, User
from flask_jwt_extended import jwt_required, get_jwt_identity

class AssignReviewerResource(Resource):
    @jwt_required()
    def post(self, conf_id):
        data = request.get_json()
        reviewer_email = data.get("email")

        if not reviewer_email:
            return {"error": "Email du reviewer requis"}, 400

        session = SessionLocal()
        try:
            # Vérifier que la conférence existe
            conference = session.query(Conference).filter_by(id=conf_id).first()
            if not conference:
                return {"error": "Conférence introuvable"}, 404

            current_user = get_jwt_identity()

            # Vérifier que l'utilisateur connecté est le créateur de la conférence
            if str(conference.creator_id) != current_user["id"]:
                return {"error": "Accès refusé (non-chair)"}, 403

            # Vérifier que le reviewer existe
            reviewer = session.query(User).filter_by(email=reviewer_email).first()
            if not reviewer:
                return {"error": "Utilisateur non trouvé"}, 404

            # Créer le rôle Reviewer
            role = ConferenceRole(
                user_id=reviewer.id,
                conference_id=conference.id,
                role_name=ConferenceRoleEnum.REVIEWER
            )

            session.add(role)
            session.commit()
            return {"message": f"{reviewer.email} a été assigné comme reviewer"}, 201

        except Exception as e:
            session.rollback()
            return {"error": f"Erreur serveur : {str(e)}"}, 500

        finally:
            session.close()

class SubmitReviewResource(Resource):
    @jwt_required()
    def post(self, paper_id):
        data = request.get_json()
        score = data.get("score")
        comments_to_author = data.get("comments_to_author")
        comments_to_committee = data.get("comments_to_committee")
        recommendation = data.get("recommendation")

        user = get_jwt_identity()
        session = SessionLocal()

        try:
            # Vérifie que le papier existe
            paper = session.query(Paper).filter_by(id=paper_id).first()
            if not paper:
                return {"error": "Papier introuvable"}, 404

            # Vérifie que l'utilisateur est reviewer de cette conférence
            is_reviewer = session.query(ConferenceRole).filter_by(
                user_id=user["id"],
                conference_id=paper.conference_id,
                role_name=ConferenceRoleEnum.REVIEWER
            ).first()

            if not is_reviewer:
                return {"error": "Vous n'êtes pas reviewer pour cette conférence"}, 403

            # Vérifie s'il a déjà évalué ce papier
            existing_review = session.query(Evaluation).filter_by(
                reviewer_id=user["id"],
                paper_id=paper.id
            ).first()

            if existing_review:
                return {"error": "Vous avez déjà évalué ce papier"}, 409

            # Créer l'évaluation
            review = Evaluation(
                reviewer_id=user["id"],
                paper_id=paper.id,
                score=score,
                comments_to_author=comments_to_author,
                comments_to_committee=comments_to_committee,
                recommendation=EvaluationRecommendationEnum(recommendation)
            )

            session.add(review)
            session.commit()
            return {"message": "Évaluation enregistrée"}, 201

        except Exception as e:
            session.rollback()
            return {"error": f"Erreur serveur : {str(e)}"}, 500

        finally:
            session.close()
class PaperReviewsResource(Resource):
    @jwt_required()
    def get(self, paper_id):
        session = SessionLocal()
        try:
            paper = session.query(Paper).filter_by(id=paper_id).first()
            if not paper:
                return {"error": "Papier introuvable"}, 404

            reviews = session.query(Evaluation).filter_by(paper_id=paper_id).all()
            result = []
            for r in reviews:
                result.append({
                    "id": str(r.id),
                    "reviewer_id": str(r.reviewer_id),
                    "score": r.score,
                    "comments_to_author": r.comments_to_author,
                    "comments_to_committee": r.comments_to_committee,
                    "recommendation": r.recommendation.value,
                    "submitted_at": str(r.submitted_at)
                })

            return result, 200

        except Exception as e:
            return {"error": f"Erreur serveur : {str(e)}"}, 500
        finally:
            session.close()


