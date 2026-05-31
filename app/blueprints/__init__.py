from app.blueprints.agent_bp import agent_bp
from app.blueprints.answer_bp import answer_bp
from app.blueprints.evaluate_bp import evaluate_bp
from app.blueprints.resource_bp import resource_bp
from app.blueprints.study_bp import study_bp
from app.blueprints.user_bp import user_bp


def register_blueprints(app) -> None:
    app.register_blueprint(user_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(resource_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(answer_bp)
    app.register_blueprint(evaluate_bp)

