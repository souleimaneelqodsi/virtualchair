from flask import g, current_app
from datetime import datetime
from ..tables import Conference, User, ConferenceRole, ConferenceRoleEnum


class ConferenceModel:
    def create_conference(
        self,
        name: str,
        description: str | None,
        start_date_str: str | None,
        end_date_str: str | None,
        location: str | None,
        submission_deadline_str: str | None,
        current_phase: str | None,
        creator_id: str,
    ) -> Conference:
        if not name: raise ValueError("Le nom de la conférence est requis.")
        if not creator_id: raise ValueError("L'identifiant du créateur est requis.")

        creator = g.db_session.get(User, creator_id)
        if not creator: raise ValueError(f"Créateur avec ID {creator_id} non trouvé.")

        start_date, end_date, submission_deadline = None, None, None
        try:
            if start_date_str: start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if end_date_str: end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if submission_deadline_str:
                submission_deadline = datetime.strptime(submission_deadline_str, "%Y-%m-%d %H:%M:%S") if submission_deadline_str else None
        except ValueError as e:
            raise ValueError(f"Format de date invalide. Détail: {e}")

        new_conference = Conference(
            name=name, description=description, start_date=start_date, end_date=end_date,
            location=location, submission_deadline=submission_deadline,
            current_phase=current_phase, creator_id=creator_id,
        )

        try:
            g.db_session.add(new_conference)
            g.db_session.flush()
            if new_conference.id is None:
                g.db_session.rollback()
                raise ValueError("Erreur critique: new_conference.id est None après flush.")

            chair_role = ConferenceRole(
                user_id=creator_id,
                conference_id=new_conference.id,
                role_name=ConferenceRoleEnum.CHAIR.value
            )
            g.db_session.add(chair_role)

            g.db_session.commit()
            g.db_session.refresh(new_conference)
            return new_conference
        except Exception as e:
            g.db_session.rollback()
            current_app.logger.error(f"Database error creating conference or assigning role: {e}", exc_info=True)
            raise ValueError(f"Erreur lors de la création de la conférence et de l'assignation du rôle: {str(e)}")

    def get_all_conferences(self):
        try:
            return g.db_session.query(Conference).order_by(Conference.created_at.desc()).all()
        except Exception as e:
            current_app.logger.error(f"Database error fetching all conferences: {e}", exc_info=True)
            raise ValueError(f"Erreur lors de la récupération des conférences: {str(e)}")

    def get_conference_by_id(self, conference_id: str):
        if not conference_id: raise ValueError("L'ID de la conférence est requis.")
        try:
            return g.db_session.get(Conference, conference_id)
        except Exception as e:
            current_app.logger.error(f"Database error fetching conference by ID {conference_id}: {e}", exc_info=True)
            raise ValueError(f"Erreur lors de la récupération de la conférence: {str(e)}")

    def is_user_chair_of_conference(self, user_id: str, conference_id: str) -> bool:
        if not user_id or not conference_id: return False
        try:


            role = g.db_session.query(ConferenceRole).filter_by(
                user_id=user_id,
                conference_id=conference_id,
                role_name=ConferenceRoleEnum.CHAIR.value
            ).first()
            return role is not None
        except Exception as e:
            current_app.logger.error(f"Error checking chair role for user {user_id} in conf {conference_id}: {e}", exc_info=True)
            return False
