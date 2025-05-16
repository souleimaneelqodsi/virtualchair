from flask import request, g, current_app
from flask_restful import Resource
from flask_login import login_required, current_user
from ..models.paper_model import PaperModel


def format_datetime_or_none(dt):
    return dt.isoformat() if dt else None

class PaperListCreateResource(Resource):
    @login_required
    def post(self, conf_uuid: str):

        if 'file' not in request.files:
            return {"error": "Aucun fichier sélectionné dans la requête."}, 400

        file = request.files['file']
        if file.filename == '':
            return {"error": "Aucun fichier sélectionné."}, 400

        data = request.form
        title = data.get("title")
        abstract = data.get("abstract")
        keywords = data.get("keywords")

        if not title:
            return {"error": "Le titre du papier est requis."}, 400

        paper_model = PaperModel()
        try:
            new_paper = paper_model.create_paper(
                title=title,
                abstract=abstract,
                keywords=keywords,
                file_storage=file,
                conference_id=conf_uuid,
                author_id=current_user.id,
            )
            return {
                "message": "Papier soumis avec succès.",
                "paper": {
                    "id": str(new_paper.id),
                    "title": new_paper.title,
                    "abstract": new_paper.abstract,
                    "keywords": new_paper.keywords,
                    "s3_file_url": new_paper.s3_file_url,
                    "status": new_paper.status.value,
                    "submitted_at": format_datetime_or_none(new_paper.submitted_at),
                    "conference_id": str(new_paper.conference_id),
                    "author_id": str(new_paper.author_id),
                },
            }, 201
        except PermissionError as e:
            current_app.logger.warning(f"Permission denied for paper submission: {e}")
            return {"error": str(e)}, 403
        except ValueError as e:
            current_app.logger.error(f"ValueError in POST /conferences/{conf_uuid}/papers: {e}")
            return {"error": str(e)}, 400
        except Exception as e:
            current_app.logger.error(f"API error in POST /conferences/{conf_uuid}/papers: {e}", exc_info=True)
            return {"error": "Erreur interne du serveur lors de la soumission du papier."}, 500

    def get(self, conf_uuid: str):
        paper_model = PaperModel()
        try:
            papers = paper_model.get_papers_for_conference(conf_uuid)
            return [{
                "id": str(p.id),
                "title": p.title,
                "status": p.status.value if p.status else None,
                "submitted_at": format_datetime_or_none(p.submitted_at),
                "author_id": str(p.author_id)
            } for p in papers], 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            current_app.logger.error(f"API error GET /conferences/{conf_uuid}/papers: {e}", exc_info=True)
            return {"error": "Erreur interne du serveur."}, 500


class PaperDetailResource(Resource):
    def get(self, conf_uuid: str, paper_uuid: str):
        paper_model = PaperModel()
        try:
            paper = paper_model.get_paper_by_id(paper_uuid)
            if not paper or str(paper.conference_id) != conf_uuid:
                return {"error": "Papier non trouvé dans cette conférence."}, 404

            return {
                "id": str(paper.id),
                "title": paper.title,
                "abstract": paper.abstract,
                "keywords": paper.keywords,
                "s3_file_url": paper.s3_file_url,
                "status": paper.status.value if paper.status else None,
                "submitted_at": format_datetime_or_none(paper.submitted_at),
                "last_modified_at": format_datetime_or_none(paper.last_modified_at),
                "conference_id": str(paper.conference_id),
                "author_id": str(paper.author_id),
            }, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            current_app.logger.error(f"API error GET /conferences/{conf_uuid}/papers/{paper_uuid}: {e}", exc_info=True)
            return {"error": "Erreur interne du serveur."}, 500
