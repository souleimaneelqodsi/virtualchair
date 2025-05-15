from flask import g
from datetime import datetime
from core.tables import Conference, User
from core.tables import ConferenceRoleEnum


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
        if not name:
            raise ValueError("Le nom de la conférence est requis.")
        if not creator_id:
            raise ValueError("L'identifiant du créateur est requis.")

        creator = g.db_session.query(User).filter_by(id=creator_id).first()
        if not creator:
            raise ValueError(f"Créateur avec ID {creator_id} non trouvé.")

        start_date, end_date, submission_deadline = None, None, None
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if submission_deadline_str:
                submission_deadline = datetime.strptime(
                    submission_deadline_str, "%Y-%m-%d %H:%M:%S"
                )
        except ValueError as e:
            raise ValueError(
                f"Format de date invalide. Utilisez YYYY-MM-DD pour les dates et YYYY-MM-DD HH:MM:SS pour les deadlines. Détail: {e}"
            )

        new_conference = Conference(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            location=location,
            submission_deadline=submission_deadline,
            current_phase=current_phase,
            creator_id=creator_id,
        )

        try:
            g.db_session.add(new_conference)
            g.db_session.commit()
            g.db_session.refresh(new_conference)
            return new_conference
        except Exception as e:
            g.db_session.rollback()

            print(f"Database error creating conference: {e}")
            raise ValueError(f"Erreur lors de la création de la conférence: {str(e)}")

    def get_all_conferences(self):
        try:
            return (
                g.db_session.query(Conference)
                .order_by(Conference.created_at.desc())
                .all()
            )
        except Exception as e:
            print(f"Database error fetching all conferences: {e}")
            raise ValueError(
                f"Erreur lors de la récupération des conférences: {str(e)}"
            )

    def get_conference_by_id(self, conference_id: str):
        if not conference_id:
            raise ValueError("L'ID de la conférence est requis.")
        try:
            return g.db_session.query(Conference).filter_by(id=conference_id).first()
        except Exception as e:
            print(f"Database error fetching conference by ID {conference_id}: {e}")
            raise ValueError(
                f"Erreur lors de la récupération de la conférence: {str(e)}"
            )

    def is_user_chair_of_conference(self, user_id: str, conference_id: str) -> bool:
        from core.tables import ConferenceRole

        if not user_id or not conference_id:
            return False
        try:
            role = (
                g.db_session.query(ConferenceRole)
                .filter_by(
                    user_id=user_id,
                    conference_id=conference_id,
                    role_name=ConferenceRoleEnum.CHAIR,
                )
                .first()
            )
            return role is not None
        except Exception as e:
            print(
                f"Error checking chair role for user {user_id} in conf {conference_id}: {e}"
            )
            return False
