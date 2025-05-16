import uuid
from flask import g, current_app
from werkzeug.utils import secure_filename
from ..tables import Paper, ConferenceRole, ConferenceRoleEnum, PaperStatusEnum, User, Conference
from datetime import datetime

class PaperModel:
    def get_user_roles_for_conference(self, user_id: str, conference_id: str):
        if not user_id or not conference_id:
            return []

        try:
            roles_objects = (
                g.db_session.query(ConferenceRole)
                .filter_by(user_id=user_id, conference_id=conference_id)
                .all()
            )
            # Assuming role_name on the ConferenceRole object is the Python enum member
            # (due to by_value=True in tables.py for reads)
            return [role.role_name.value for role in roles_objects if role.role_name]
        except Exception as e:
            current_app.logger.error(f"Error fetching user roles for user {user_id} in conference {conference_id}: {e}", exc_info=True)
            return []


    def can_submit_to_conference(self, user_id: str, conference_id: str) -> bool:
        user_roles_strings = self.get_user_roles_for_conference(user_id, conference_id)
        if ConferenceRoleEnum.CHAIR.value in user_roles_strings or \
           ConferenceRoleEnum.REVIEWER.value in user_roles_strings:
            return False
        return True

    def _upload_to_s3(self, file_storage, conference_id: str, paper_id: str) -> str | None:
        if not g.s3_client or not file_storage:
            current_app.logger.warning("S3 client not configured (from g.s3_client) or no file provided for upload.")
            return None

        original_filename = secure_filename(file_storage.filename)
        file_extension = ""
        if '.' in original_filename:
            file_extension = original_filename.rsplit('.', 1)[1].lower()

        s3_filename = f"paper_{paper_id}.{file_extension}" if file_extension else f"paper_{paper_id}"
        s3_key = f"conferences/{conference_id}/papers/{s3_filename}"

        try:
            g.s3_client.upload_fileobj(
                file_storage,
                current_app.config["S3_BUCKET_NAME"],
                s3_key,
                ExtraArgs={'ContentType': file_storage.content_type or 'application/octet-stream'}
            )
            s3_url = f"https://{current_app.config['S3_BUCKET_NAME']}.s3.{current_app.config['AWS_REGION']}.amazonaws.com/{s3_key}"
            current_app.logger.info(f"Successfully uploaded {s3_key} to S3.")
            return s3_url
        except Exception as e:
            current_app.logger.error(f"S3 Upload failed for key {s3_key}: {e}", exc_info=True)
            raise ValueError(f"Erreur lors du téléversement du fichier sur S3: {str(e)}")


    def create_paper(
        self,
        title: str,
        abstract: str | None,
        keywords: str | None,
        file_storage,
        conference_id: str,
        author_id: str,
    ) -> Paper:
        if not title: raise ValueError("Le titre du papier est requis.")
        if not conference_id: raise ValueError("L'ID de la conférence est requis.")
        if not author_id: raise ValueError("L'ID de l'auteur est requis.")
        if not file_storage or not file_storage.filename:
            raise ValueError("Un fichier valide est requis pour la soumission.")

        conference = g.db_session.get(Conference, conference_id)
        if not conference: raise ValueError(f"Conférence avec ID {conference_id} non trouvée.")

        author = g.db_session.get(User, author_id)
        if not author: raise ValueError(f"Auteur avec ID {author_id} non trouvé.")

        if not self.can_submit_to_conference(user_id=author_id, conference_id=conference_id):
            raise PermissionError("L'utilisateur n'est pas autorisé à soumettre un papier à cette conférence (rôle Chair ou Reviewer).")

        new_paper_id = uuid.uuid4()
        s3_url = self._upload_to_s3(file_storage, conference_id, str(new_paper_id))
        if not s3_url: raise ValueError("Le téléversement du fichier a échoué.")

        new_paper = Paper(
            id=new_paper_id,
            title=title,
            abstract=abstract,
            keywords=keywords,
            s3_file_url=s3_url,
            status=PaperStatusEnum.SUBMITTED, # Explicitly assign the string value "Submitted"
            conference_id=conference_id,
            author_id=author_id,
            submitted_at=datetime.utcnow()
        )

        current_author_roles_strings = self.get_user_roles_for_conference(user_id=author_id, conference_id=conference_id)
        if ConferenceRoleEnum.AUTHOR.value not in current_author_roles_strings:
            author_role_entry = ConferenceRole(
                user_id=author_id,
                conference_id=conference_id,
                role_name=ConferenceRoleEnum.AUTHOR.value # Explicitly assign the string value "Author"
            )
            g.db_session.add(author_role_entry)

        try:
            g.db_session.add(new_paper)
            g.db_session.commit()
            g.db_session.refresh(new_paper)
            return new_paper
        except Exception as e:
            g.db_session.rollback()
            current_app.logger.error(f"Database error creating paper: {e}", exc_info=True)
            raise ValueError(f"Erreur lors de la création du papier dans la base de données: {str(e)}")

    def get_papers_for_conference(self, conference_id: str):
        if not conference_id: raise ValueError("L'ID de la conférence est requis.")
        try:
            return g.db_session.query(Paper).filter_by(conference_id=conference_id).order_by(Paper.submitted_at.desc()).all()
        except Exception as e:
            current_app.logger.error(f"Error fetching papers for conference {conference_id}: {e}", exc_info=True)
            raise ValueError(f"Erreur lors de la récupération des papiers: {str(e)}")

    def get_paper_by_id(self, paper_id: str):
        if not paper_id: raise ValueError("L'ID du papier est requis.")
        try:
            return g.db_session.get(Paper, paper_id)
        except Exception as e:
            current_app.logger.error(f"Error fetching paper by ID {paper_id}: {e}", exc_info=True)
            raise ValueError(f"Erreur lors de la récupération du papier: {str(e)}")
