from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)  # For hashed password
    is_provider = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(50), nullable=True)
    otp = db.Column(db.String(6), nullable=True)  # Stores the OTP
    otp_expiration = db.Column(db.DateTime, nullable=True)  # Stores OTP expiration time


    # Relationships
    patient_info = db.relationship('Patient', backref='user', uselist=False)
    patient_records_created = db.relationship('PatientRecord', backref='creator', lazy=True, foreign_keys='PatientRecord.user_id')
    patient_records = db.relationship('PatientRecord', backref='doctor', lazy=True, foreign_keys='PatientRecord.doctor_id')
    medical_records = db.relationship('MedicalRecord', backref='creator', lazy=True, foreign_keys='MedicalRecord.user_id')
    appointments_as_patient = db.relationship('AppointmentRequest', backref='patient_requester', lazy=True, foreign_keys='AppointmentRequest.user_id')
    appointments_as_provider = db.relationship('Appointment', backref='appointment_provider', lazy=True, foreign_keys='Appointment.provider_id')
    
    
    # Update prescriptions relationships with primaryjoin
    prescriptions_as_patient = db.relationship(
        'Prescription',
        backref='prescription_patient',
        lazy=True,
        foreign_keys='Prescription.patient_id',
        primaryjoin="User.id == Prescription.patient_id"
    )
    prescriptions_as_provider = db.relationship(
        'Prescription',
        backref='prescription_provider',
        lazy=True,
        foreign_keys='Prescription.provider_id',
        primaryjoin="User.id == Prescription.provider_id"
    )
    
    admissions_made = db.relationship('AdmissionRecord', backref='admitting_doctor', lazy=True, foreign_keys='AdmissionRecord.doctor_id')
    discharges_made = db.relationship('DischargeRecord', backref='discharging_doctor', lazy=True, foreign_keys='DischargeRecord.doctor_id')

    def __repr__(self):
        return f'<User {self.username} - Role: {self.role}>'

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, plaintext_password):
        self.password_hash = generate_password_hash(plaintext_password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def generate_otp(self):
        import random
        otp = f"{random.randint(100000, 999999)}"  # Generate a 6-digit OTP
        self.otp = otp
        self.otp_expiration = datetime.utcnow() + timedelta(minutes=15)  # Set OTP expiration for 15 minutes
        db.session.commit()
        return otp

    def verify_otp(self, otp):
        if self.otp == otp and self.otp_expiration >= datetime.utcnow():
            self.otp = None  # Clear OTP after successful verification
            self.otp_expiration = None
            db.session.commit()
            return True
        return False

    def save(self):
        db.session.add(self)
        db.session.commit()



class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    is_admitted = db.Column(db.Boolean, default=False)

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    bed_id = db.Column(db.Integer, db.ForeignKey('bed.id'), nullable=True)

    room = db.relationship('Room', backref='patients', lazy=True)
    bed = db.relationship('Bed', backref='patients', lazy=True)

     # Add a property to calculate the patient's age
    @property
    def age(self):
        if self.dob:
            today = datetime.today()
            age = today.year - self.dob.year
            if today.month < self.dob.month or (today.month == self.dob.month and today.day < self.dob.day):
                age -= 1
            return age
        return None  # Return None if dob is not available

    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'


class PatientRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease = db.Column(db.String(100)) 
    diagnosis = db.Column(db.Text, nullable=True)
    prescribed_medicine = db.Column(db.String(255)) 
    notes = db.Column(db.Text)
    follow_up_date = db.Column(db.Date) 
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)

    patient = db.relationship('Patient', backref='records', lazy=True)

    def __repr__(self):
        return f'<PatientRecord {self.id} - {self.record_date}>'


class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    summary = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=False)

    patient = db.relationship('Patient', backref='medical_records', lazy=True)

    def __repr__(self):
        return f'<MedicalRecord {self.id} - {self.date}>'


class AppointmentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_time = db.Column(db.DateTime, nullable=False)
    specialization_needed = db.Column(db.String(100), nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')

    patient = db.relationship('Patient', backref='appointment_requests', lazy=True)

    def __repr__(self):
        return f'<AppointmentRequest {self.id} - Status: {self.status}>'


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_request_id = db.Column(db.Integer, db.ForeignKey('appointment_request.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    patient_request = db.relationship('AppointmentRequest', backref='appointments', lazy=True)

    def __repr__(self):
        return f'<Appointment {self.id} - Provider: {self.provider_id}>'


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prescription_date = db.Column(db.DateTime, default=datetime.utcnow)
    medication_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text)
    attended_by_nurse = db.Column(db.Boolean, default=False, nullable=False)
    nurse_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    attended_date = db.Column(db.DateTime)

    patient = db.relationship('Patient', backref='prescriptions', lazy=True)

    def __repr__(self):
        return f'<Prescription {self.id} - Medication: {self.medication_name}>'


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.id} - Action: {self.action}>'


class HealthMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    metric_type = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    measurement_date = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='health_metrics', lazy=True)

    def __repr__(self):
        return f'<HealthMetrics {self.id} - Type: {self.metric_type}, Value: {self.value}>'


class AdmissionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='admissions', lazy=True)

    def __repr__(self):
        return f'<AdmissionRecord {self.id}>'


class DischargeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    discharge_date = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='discharges', lazy=True)

    def __repr__(self):
        return f'<DischargeRecord {self.id}>'


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    bed_count = db.Column(db.Integer, nullable=False)

  

    def __repr__(self):
        return f'<Room {self.room_number} - Bed Count: {self.bed_count}>'

    def is_full(self):
        """Check if the room is full based on the number of patients assigned."""
        return len(self.patients) >= self.bed_count
    @property
    def patient_count(self):
        """Returns the count of patients in this room."""
        return len(self.patients)



class Bed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    bed_number = db.Column(db.String(10), nullable=False)

    room = db.relationship('Room', backref='beds', lazy=True)
    def free_up(self):
        self.patient_id = None

    def __repr__(self):
        return f'<Bed {self.bed_number} - Room: {self.room_id}>'
    
