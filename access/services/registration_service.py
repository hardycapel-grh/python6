from ui.components.logger import logger


class RegistrationService:
    def __init__(self, user_service):
        self.user_service = user_service  # store the dependency

    def validate(self, username, email, password, confirm):
        if not username or not email or not password:
            return False, "All fields are required"

        if password != confirm:
            return False, "Passwords do not match"

        if self.user_service.mongo.username_exists(username):
            return False, "That username is already taken"

        if self.user_service.mongo.email_exists(email):
            return False, "That email address is already registered"

        return True, None



    def register_user(self, username, email, password):
        try:
            # Build a complete user document using MongoService's unified builder
            user_doc = self.user_service.mongo.build_user_document(
                username=username,
                email=email,
                password=password,
                status="Active"
            )

            # Insert into database
            self.user_service.mongo.create_user(
                user_doc,
                performed_by="self-register"
            )

            logger.info(f"User '{username}' registered successfully")

        except Exception as e:
            raise RuntimeError(f"Registration failed: {e}")
