from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, DateTimeField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models import User  # Assuming your models are in app.models

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Admin Registration Form
class AdminRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('doctor', 'Doctor'), ('nurse', 'Nurse')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    specialization = StringField('Specialization', validators=[DataRequired()])  # Added specialization field
    submit = SubmitField('Register Medic')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already in use. Please choose another one.')

# Nurse-specific form for registering patients
class NursePatientRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    address = StringField('Address', validators=[Length(max=250)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register Patient')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already in use by a patient. Please choose another one.')

# Form for updating patient records
class UpdatePatientRecordForm(FlaskForm):
    notes = TextAreaField('Patient Notes', validators=[DataRequired()])
    prescribed_medicine = StringField('Prescribed Medicine', validators=[DataRequired()])
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    follow_up_date = DateField('Follow-up Date', format='%Y-%m-%d', validators=[DataRequired()])
    disease = StringField('Disease', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[Optional()])  # Add this
    treatment_plan = TextAreaField('Treatment Plan', validators=[DataRequired()])
    treatment = TextAreaField('Treatment', validators=[DataRequired()])
    submit = SubmitField('Update Record')
# Form for patients to request an appointment
class AppointmentRequestForm(FlaskForm):
    reason = StringField('Reason for Appointment', validators=[DataRequired()])
    specialization = SelectField('Specialization Needed', choices=[
        ('tooth', 'Tooth'),
        ('eye', 'Eye'),
        ('ear', 'Ear'),
        # Add more specializations as necessary
    ], validators=[DataRequired()])  # Added specialization field
    requested_time = DateTimeField('Requested Appointment Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Request Appointment')

# Form for scheduling an appointment based on patient requests
class ScheduleAppointmentForm(FlaskForm):
    patient_request_id = StringField('Patient Request ID', validators=[DataRequired()])
    provider_id = StringField('Provider ID', validators=[DataRequired()])
    appointment_date = DateTimeField('Appointment Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Schedule Appointment')

# Provider form for managing provider information
class ProviderForm(FlaskForm):
    provider_name = StringField('Provider Name', validators=[DataRequired()])
    specialty = StringField('Specialty', validators=[Length(max=100)])
    contact_number = StringField('Contact Number', validators=[Length(max=15)])
    submit = SubmitField('Save Provider Details')

# Prescription form for doctors to issue prescriptions
class PrescriptionForm(FlaskForm):
    patient_id = StringField('Patient ID', validators=[DataRequired()])
    provider_id = StringField('Provider ID', validators=[DataRequired()])
    prescription_date = DateTimeField(
        'Prescription Date', 
        format='%Y-%m-%d %H:%M:%S.%f', 
        validators=[DataRequired()]
    )
    medication_name = StringField('Medication Name', validators=[DataRequired()])
    dosage = StringField('Dosage', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[Length(max=500)])
    submit = SubmitField('Save Prescription')

# Form for recording health metrics (e.g., vital signs)
class HealthMetricsForm(FlaskForm):
    metric_type = StringField('Metric Type', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired()])
    measurement_date = DateField('Measurement Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Save Metric')

# Admin form for assigning roles
class AssignRoleForm(FlaskForm):
    user_id = StringField('User ID', validators=[DataRequired()])
    role_name = SelectField('Role Name', choices=[('admin', 'Admin'), ('doctor', 'Doctor'), ('nurse', 'Nurse'), ('patient', 'Patient')], validators=[DataRequired()])
    submit = SubmitField('Assign Role')

# Form for querying the audit log
class AuditLogQueryForm(FlaskForm):
    user_id = StringField('User ID')
    action = StringField('Action')
    start_date = DateField('Start Date', format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d')
    submit = SubmitField('Search Logs')

# Form for creating medic accounts
class CreateMedicForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('doctor', 'Doctor'), ('nurse', 'Nurse')], validators=[DataRequired()])
    specialization = SelectField(
        'Specialization', 
        choices=[
            ('cardiologist', 'Cardiologist'),
            ('dermatologist', 'Dermatologist'),
            ('neurologist', 'Neurologist'),
            ('pediatrician', 'Pediatrician'),
            ('psychiatrist', 'Psychiatrist'),
            ('surgeon', 'Surgeon'),
            ('orthopedist', 'Orthopedist'),
            ('gynecologist', 'Gynecologist'),
            ('general_practitioner', 'General Practitioner'),
            # Add more specializations as needed
        ],
        validators=[DataRequired()],
        default='general_practitioner'  # Optional default value
    )
    submit = SubmitField('Create Medic')


# Form for creating patient accounts
class CreatePatientForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    address = StringField('Address', validators=[Length(max=250)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('patient', 'Patient')], validators=[DataRequired()])
    submit = SubmitField('Add Patient')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already in use. Please choose another one.')

# Form for users to change their password
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

# Form for registering patients
class PatientRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=35)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    address = TextAreaField('Address', validators=[Optional()])
    submit = SubmitField('Register Patient')

# Form for editing user information
class EditUserForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('doctor', 'Doctor'), ('nurse', 'Nurse'), ('patient', 'Patient')], validators=[DataRequired()])
    specialization = SelectField(
        'Specialization', 
        choices=[
            ('cardiologist', 'Cardiologist'),
            ('dermatologist', 'Dermatologist'),
            ('neurologist', 'Neurologist'),
            ('pediatrician', 'Pediatrician'),
            ('psychiatrist', 'Psychiatrist'),
            ('surgeon', 'Surgeon'),
            ('orthopedist', 'Orthopedist'),
            ('gynecologist', 'Gynecologist'),
            ('general_practitioner', 'General Practitioner'),
            # Add more specializations as needed
        ],
        validators=[DataRequired()],
        default='general_practitioner'  # Optional default value
    )
    submit = SubmitField('Create Medic')
    submit = SubmitField('Update User')

# Form for creating or updating patient records
class PatientRecordForm(FlaskForm):
    record_date = DateField('Record Date', format='%Y-%m-%d', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired(), Length(max=500)])
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired(), Length(max=500)])
    treatment_plan = TextAreaField('Treatment Plan', validators=[Length(max=500)])
    vitals = TextAreaField('Vitals', validators=[DataRequired()])
    submit = SubmitField('Save Record')

# Form for assigning rooms and beds to patients
class AssignRoomBedForm(FlaskForm):
    patient_id = StringField('Patient ID', validators=[DataRequired()])
    room_number = StringField('Room Number', validators=[DataRequired()])
    bed_number = StringField('Bed Number', validators=[DataRequired()])
    submit = SubmitField('Assign Room and Bed')
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    # New fields added
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    
    submit = SubmitField('Register')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class VerifyOTPForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired(), Length(6, 6)])
    submit = SubmitField('Verify OTP')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')