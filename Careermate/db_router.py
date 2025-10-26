"""
Database router to direct job-related queries to PostgreSQL
and feedback/other data to SQLite
"""

class PostgresRouter:
    """
    Route database operations for recommendation_agent models to PostgreSQL database.
    """

    postgres_apps = {'recommendation_agent'}  # Apps that use PostgreSQL
    postgres_models = {'JobPosting', 'JobDescription', 'JDSkill', 'CandidateInfo',
                      'Account', 'Recruiter', 'JobApply', 'JobFeedback'}

    def db_for_read(self, model, **hints):
        """Direct read operations for recommendation_agent models to PostgreSQL"""
        if model._meta.app_label in self.postgres_apps:
            return 'postgres'
        return 'default'

    def db_for_write(self, model, **hints):
        """Direct write operations for recommendation_agent models to PostgreSQL"""
        if model._meta.app_label in self.postgres_apps:
            return 'postgres'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if both models are in the same database"""
        db_set = {'postgres', 'default'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure recommendation_agent models migrations only run on PostgreSQL"""
        if app_label in self.postgres_apps:
            return db == 'postgres'
        return db == 'default'
