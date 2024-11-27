"""Add nurse attendance fields to Prescription

Revision ID: 5826cf286716
Revises: 
Create Date: 2024-11-26 10:53:33.263959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5826cf286716'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('room',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room_number', sa.String(length=10), nullable=False),
    sa.Column('bed_count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('room_number')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('password_hash', sa.String(length=150), nullable=False),
    sa.Column('is_provider', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('specialization', sa.String(length=50), nullable=True),
    sa.Column('otp', sa.String(length=6), nullable=True),
    sa.Column('otp_expiration', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('audit_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('details', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bed',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=False),
    sa.Column('bed_number', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('patient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('dob', sa.Date(), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('is_admitted', sa.Boolean(), nullable=True),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.Column('bed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bed_id'], ['bed.id'], ),
    sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('admission_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('admission_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('appointment_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('requested_time', sa.DateTime(), nullable=False),
    sa.Column('specialization_needed', sa.String(length=100), nullable=True),
    sa.Column('reason', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('discharge_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('discharge_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('health_metrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('metric_type', sa.String(length=100), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('measurement_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medical_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('summary', sa.String(length=200), nullable=False),
    sa.Column('details', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('patient_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('disease', sa.String(length=100), nullable=True),
    sa.Column('diagnosis', sa.Text(), nullable=True),
    sa.Column('prescribed_medicine', sa.String(length=255), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('follow_up_date', sa.Date(), nullable=True),
    sa.Column('record_date', sa.DateTime(), nullable=True),
    sa.Column('details', sa.Text(), nullable=False),
    sa.Column('treatment', sa.Text(), nullable=True),
    sa.Column('treatment_plan', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prescription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.Column('prescription_date', sa.DateTime(), nullable=True),
    sa.Column('medication_name', sa.String(length=150), nullable=False),
    sa.Column('dosage', sa.String(length=100), nullable=False),
    sa.Column('instructions', sa.Text(), nullable=True),
    sa.Column('attended_by_nurse', sa.Boolean(), nullable=False),
    sa.Column('nurse_id', sa.Integer(), nullable=True),
    sa.Column('attended_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['nurse_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.ForeignKeyConstraint(['provider_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('appointment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_request_id', sa.Integer(), nullable=False),
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.Column('appointment_date', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['patient_request_id'], ['appointment_request.id'], ),
    sa.ForeignKeyConstraint(['provider_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('appointment')
    op.drop_table('prescription')
    op.drop_table('patient_record')
    op.drop_table('medical_record')
    op.drop_table('health_metrics')
    op.drop_table('discharge_record')
    op.drop_table('appointment_request')
    op.drop_table('admission_record')
    op.drop_table('patient')
    op.drop_table('bed')
    op.drop_table('audit_log')
    op.drop_table('user')
    op.drop_table('room')
    # ### end Alembic commands ###
