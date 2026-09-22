from .. import db


class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(100), nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
