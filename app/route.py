from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Appointment, PatientRecord, MedicalRecord, Patient, Prescription, AppointmentRequest,AuditLog, AdmissionRecord, DischargeRecord, HealthMetrics, Room, Bed
from app.forms import (
    LoginForm, ChangePasswordForm, CreateMedicForm, EditUserForm, 
    PatientRecordForm, ScheduleAppointmentForm, UpdatePatientRecordForm, PatientRegistrationForm, PrescriptionForm, RegistrationForm, RequestResetForm, VerifyOTPForm, ResetPasswordForm
)
from app import db
import logging

# Main blueprint
main_bp = Blueprint('main', __name__)

# Initialize logging
logger = logging.getLogger(__name__)


@main_bp.route('/patient/view-appointments')
@login_required
def view_appointments():
    # Ensure the current user has a patient profile
    patient = current_user.patient_info
    if not patient:
        flash('You do not have a patient profile.', 'danger')
        return redirect(url_for('main.patient_dashboard'))

    # Retrieve all appointment requests for this patient by using their patient ID
    appointment_requests = db.session.query(AppointmentRequest).filter_by(patient_id=patient.id).all()

    # Collect appointments linked to each appointment request
    appointments = []
    for request in appointment_requests:
        appointments.extend(request.appointments)  # Collect associated Appointment entries

    return render_template('view_appointments.html', appointments=appointments)



@main_bp.route('/')
def index():
    return render_template('index.html')
# Doctor's route to list patients
@main_bp.route('/doctor/patients', methods=['GET'])
@login_required
def list_patients_doctor():
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Query only 'User' entries with role 'patient' and associated patient_info
    patients = User.query.filter_by(role='patient').join(Patient, User.id == Patient.user_id).all()

    return render_template('list_patients2.html', patients=patients)


from datetime import datetime

@main_bp.route('/doctor/prescribe/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def prescribe_medicine(patient_id):
    if current_user.role != 'doctor':
        logger.warning(f"Unauthorized access attempt by user {current_user.id} for prescribing to patient {patient_id}.")
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Fetch the User instance
    try:
        user = User.query.get_or_404(patient_id)
        logger.info(f"User {user.id} ({user.username}) retrieved successfully for patient prescription.")
    except Exception as e:
        logger.error(f"Error fetching user with ID {patient_id}: {e}")
        flash('Error fetching patient data.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Check if the patient exists in the Patient table
    patient = Patient.query.filter_by(user_id=user.id).first()

    if not patient:
        logger.info(f"Patient not found for user {user.id}. Creating new Patient record.")
        try:
            patient = Patient(
                user_id=user.id,
                first_name=user.username,
                last_name=user.username,
                dob=datetime(2000, 1, 1),  # Placeholder DOB; update based on actual data
                phone_number=None,
                address=None
            )
            db.session.add(patient)
            db.session.commit()
            logger.info(f"New patient record created for {user.username}.")
            flash(f"Patient {user.username} added successfully.", 'success')
        except Exception as e:
            logger.error(f"Error creating patient record for user {user.id}: {e}")
            flash('Error creating patient record.', 'danger')
            return redirect(url_for('main.doctor_dashboard'))

    # Fetch existing medical records for the patient
    existing_records = PatientRecord.query.filter_by(patient_id=patient.id).all()

    if not existing_records:
        logger.warning(f"No medical records found for patient {patient.id}. Redirecting to add records.")
        flash('No medical records found for this patient. Please add a medical record before prescribing medicine.', 'warning')
        return redirect(url_for('main.add_patient_record', patient_id=patient.id))

    # Initialize the form
    form = PrescriptionForm()

    # Populate hidden fields
    form.patient_id.data = patient.id
    form.provider_id.data = current_user.id
    form.prescription_date.data = datetime.utcnow()  # Ensures precision up to microseconds

    # Force prescription_date to a specific format and log it
    formatted_date = form.prescription_date.data.strftime('%Y-%m-%d %H:%M:%S.%f')
    logger.info(f"Form data: {form.data}, formatted_date: {formatted_date}")

    if form.validate_on_submit():
        try:
            # Validate and log formatted prescription_date before saving
            prescription_date = form.prescription_date.data
            if isinstance(prescription_date, datetime):
                logger.debug(f"Valid prescription_date: {prescription_date} ({prescription_date.strftime('%Y-%m-%d %H:%M:%S.%f')})")
            else:
                raise ValueError("Invalid datetime format for prescription_date.")

            # Create the Prescription object
            prescription = Prescription(
                patient_id=form.patient_id.data,
                provider_id=form.provider_id.data,
                prescription_date=prescription_date,
                medication_name=form.medication_name.data,
                dosage=form.dosage.data,
                instructions=form.instructions.data
            )

            # Log the prescription object
            logger.debug(f"Prescription object: {prescription}")

            # Add to database
            db.session.add(prescription)
            db.session.commit()

            logger.info(f"Prescription added successfully for patient {patient.id} by provider {current_user.id}.")
            flash('Prescription added successfully!', 'success')
            return redirect(url_for('main.doctor_dashboard', patient_id=patient.id))

        except Exception as e:
            logger.error(f"Error adding prescription for patient {patient.id}: {e}")
            flash('Error adding prescription. Please try again.', 'danger')

    else:
        # Log form errors if validation fails
        if form.errors:
            logger.error(f"Form validation errors: {form.errors}")

    return render_template('prescribe_medicine.html', form=form, patient=patient)




@main_bp.route('/doctor/update_record/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def update_patient_record(patient_id):
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    patient = User.query.get_or_404(patient_id)
    form = UpdatePatientRecordForm()

    # Check if there are existing medical records for the patient
    existing_records = PatientRecord.query.filter_by(patient_id=patient.id).all()
    
    if not existing_records:
        flash('No medical records found for this patient. Please add a new record first.', 'warning')
        return redirect(url_for('main.add_patient_record', patient_id=patient.id))

    # Retrieve the first (or relevant) patient record
    record = existing_records[0]

    if form.validate_on_submit():
        # Update the record with form data
        record.disease = form.disease.data
        record.prescribed_medicine = form.prescribed_medicine.data
        record.diagnosis = form.diagnosis.data
        record.notes = form.notes.data
        record.follow_up_date = form.follow_up_date.data  # Should be in correct date format already
        record.treatment_plan = form.treatment_plan.data
        record.treatment = form.treatment.data

        db.session.commit()  # Commit changes to the database

        flash('Patient record updated successfully!', 'success')
        return redirect(url_for('main.doctor_dashboard', patient_id=patient.id))

    # Populate form with existing record data for GET request
    if request.method == 'GET':
        form.disease.data = record.disease
        form.prescribed_medicine.data = record.prescribed_medicine
        form.diagnosis.data = record.diagnosis
        form.notes.data = record.notes
        form.follow_up_date.data = record.follow_up_date  # Flask-WTForms handles date formatting
        form.treatment_plan.data = record.treatment_plan
        form.treatment.data = record.treatment

    return render_template('update_patient_record.html', form=form, patient=patient)
@main_bp.route('/doctor/add_patient_record/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def add_patient_record(patient_id):
    # Ensure the user is a doctor
    if current_user.role != 'doctor':
        logger.warning(f"Unauthorized access attempt by user {current_user.id} to add patient record.")
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    try:
        # Fetch the corresponding Patient instance
        patient = Patient.query.get(patient_id)
        
        # If the patient does not exist, automatically create a new Patient entry from the User data
        if not patient:
            patient_user = User.query.filter_by(id=patient_id, role='patient').first_or_404()

            # Automatically create a new Patient entry using the relevant data from User
            patient = Patient(
                user_id=patient_user.id,
                first_name=patient_user.username,  # Assuming username is used as a placeholder for the first name
                last_name=patient_user.username,   # Assuming username is used as a placeholder for the last name
                dob=None,  # You may want to handle the date of birth differently if it's not available
                phone_number=None,  # You can pull this from User if it's in the `User` model, or leave it empty
                address=None,  # Same as phone_number
                is_admitted=False
            )

            # Add the new patient to the database
            db.session.add(patient)
            db.session.commit()
            logger.info(f"Patient created for User ID {patient_user.id} and added to Patient table.")

        logger.info(f"Patient {patient.id} ({patient.first_name} {patient.last_name}) retrieved successfully.")

        # Initialize the form
        form = UpdatePatientRecordForm()

        # Process form submission
        if form.validate_on_submit():
            logger.debug("Form validation passed. Creating a new PatientRecord.")

            # Create the PatientRecord instance
            new_record = PatientRecord(
                patient_id=patient.id,
                user_id=patient.user_id,  # Automatically link the patient's user_id
                doctor_id=current_user.id,  # Link the record to the current doctor
                disease=form.disease.data,
                diagnosis=form.diagnosis.data,  # Ensure this field exists in your form
                prescribed_medicine=form.prescribed_medicine.data,
                notes=form.notes.data,
                follow_up_date=form.follow_up_date.data,
                details=form.details.data,  # Ensure this field exists in your form
                treatment=form.treatment.data,  # Ensure this field exists in your form
                treatment_plan=form.treatment_plan.data,  # Ensure this field exists in your form
            )

            # Add the new record to the database
            db.session.add(new_record)
            db.session.commit()
            logger.info(f"New PatientRecord created successfully for Patient ID {patient.id} by Doctor ID {current_user.id}.")
            flash('Medical record added successfully!', 'success')

            return redirect(url_for('main.view_patient_records', patient_id=patient.id))

        # Log form errors if any
        if form.errors:
            logger.error(f"Form validation errors: {form.errors}")

    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Error while adding PatientRecord for Patient ID {patient_id}: {e}")
        flash('An error occurred. Please try again.', 'danger')

    # Render the form with existing patient data
    return render_template('add_patient_record.html', patient=patient, form=form)





# Edit Medical Record
@main_bp.route('/medical_record/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_medical_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    
    if request.method == 'POST':
        # Handle form submission to update the record
        # Example:
        record.summary = request.form['summary']
        # ... update other fields as needed
        db.session.commit()
        flash('Medical record updated successfully!', 'success')
        return redirect(url_for('main.view_medical_record', record_id=record.id))
    
    return render_template('edit_medical_record.html', record=record)

# Create New Medical Record
@main_bp.route('/patient/<int:patient_id>/medical_record/new', methods=['GET', 'POST'])
@login_required
def create_medical_record(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        # Handle form submission to create a new record
        summary = request.form['summary']
        new_record = MedicalRecord(summary=summary, patient_id=patient.id)
        db.session.add(new_record)
        db.session.commit()
        flash('New medical record created successfully!', 'success')
        return redirect(url_for('main.view_medical_record', record_id=new_record.id))
    
    return render_template('create_medical_record.html', patient=patient)
# View Patients (Nurses can view the patients)
@main_bp.route('/nurse/patients')
@login_required
def list_patients_nurse():
    if 'nurse' not in current_user.role:
        flash("Unauthorized access", 'danger')
        return redirect(url_for('index'))

    patients = Patient.query.all()  # Fetch all patients
    return render_template('nurse_list_patients.html', patients=patients)

# View Prescriptions for a specific patient
@main_bp.route('/nurse/prescriptions/<int:patient_id>')
@login_required
def view_prescriptions_nurse(patient_id):
    if 'nurse' not in current_user.role:
        flash("Unauthorized access", 'danger')
        return redirect(url_for('index'))

    patient = Patient.query.get_or_404(patient_id)
    prescriptions = Prescription.query.filter_by(patient_id=patient.id).all()
    
    return render_template('nurse_view_prescriptions.html', patient=patient, prescriptions=prescriptions)
@main_bp.route('/prescription/confirm_attendance/<int:prescription_id>', methods=['POST'])
@login_required
def confirm_attendance(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)

    if not current_user.is_authenticated or current_user.role != 'nurse':
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('main.nurse_dashboard', prescription_id=prescription_id))

    # Update prescription attendance information
    prescription.attended_by_nurse = True
    prescription.nurse_id = current_user.id
    prescription.attended_date = datetime.utcnow()

    db.session.commit()
    flash('Patient has been marked as attended.', 'success')

    return redirect(url_for('main.nurse_dashboard'))
# Update Patient Records (e.g., vitals, routine checkups)
@main_bp.route('/nurse/update_record/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def update_patient_record_nurse(patient_id):
    # Ensure only users with 'nurse' role can access
    if current_user.role != 'nurse':
        flash("Unauthorized access", 'danger')
        return redirect(url_for('main.index'))

    # Fetch the patient to be updated
    patient = Patient.query.get_or_404(patient_id)

    # Initialize the form with existing patient data
    form = PatientRecordForm(obj=patient)

    # If the form is submitted and validated
    if form.validate_on_submit():
        patient.vitals = form.vitals.data  # Update patient vitals or other nurse-accessible fields
        db.session.commit()
        flash('Patient record updated successfully', 'success')
        return redirect(url_for('main.nurse_dashboard'))  # Redirect based on role
    
    # Render the form for GET request
    return render_template('nurse_update_record.html', patient=patient, form=form)

# Nurse's route to list patients
# Nurse Dashboard
@main_bp.route('/nurse/dashboard')
@login_required
def nurse_dashboard():
    if 'nurse' not in current_user.role:
        flash("Unauthorized access", 'danger')
        return redirect(url_for('index'))
    
    # Fetch list of patients for the nurse to view
    patients = Patient.query.all()
    patient_count = len(patients)

    # Fetch recent activities logged in the AuditLog
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()

    return render_template('nurse_dashboard.html', patients=patients, patient_count=patient_count, recent_activity=recent_activity)


# Doctor's route to add a patient
@main_bp.route('/doctor/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    form = PatientRegistrationForm()  # Create an instance of the patient registration form
    if form.validate_on_submit():
        # Hash the password before storing it using a valid method
        hashed_password = generate_password_hash(form.password.data)  # Use the default method (pbkdf2:sha256)

        logger.info(f"Attempting to add patient with username: {form.username.data}, email: {form.email.data}")

        # Create a new User instance
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,  # Use the hashed password
            role='patient'  # Setting the role directly as 'patient'
        )
        
        db.session.add(new_user)  # Add the user to the session
        db.session.commit()  # Commit to the database to get the user ID
        
        # Create a new Patient instance linked to the newly created User
        new_patient = Patient(
            user_id=new_user.id,  # Link to the User
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            phone_number=form.phone_number.data,
            address=form.address.data
        )

        db.session.add(new_patient)  # Add the patient to the session
        db.session.commit()  # Commit to save the patient

        flash('Patient added successfully!', 'success')
        return redirect(url_for('main.list_patients_doctor'))  # Redirect to the doctor patient list

    return render_template('add_patient.html', form=form)  # Render the form template


# Admin routes
@main_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized access attempt by user {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    logger.info(f"Admin dashboard accessed by user {current_user.username}")
    return render_template('admin_dashboard.html', admin=current_user)

# Nurse's route to view a specific patient
@main_bp.route('/nurse/view_patient/<int:patient_id>', methods=['GET'])
@login_required
def view_patient(patient_id):
    if current_user.role != 'nurse':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.nurse_dashboard'))

    patient = User.query.filter_by(id=patient_id, role='patient').first_or_404()  # Ensure patient exists
    medical_records = MedicalRecord.query.filter_by(patient_id=patient_id).all()  # Get the patient's medical records
    
    return render_template('view_patient.html', patient=patient, medical_records=medical_records)

@main_bp.route('/patients/<int:patient_id>/records', methods=['GET'])
@login_required
def view_patient_records(patient_id):
    # Fetch the patient record based on the patient_id
    patient = Patient.query.get_or_404(patient_id)

    # Fetch the associated user record
    user = patient.user  # Access the User via the relationship in the Patient model

    # Fetch the patient's medical records
    patient_records = PatientRecord.query.filter_by(patient_id=patient.id).all()

    # Logic to display patient records
    return render_template('patient_records.html', patient=patient, user=user, records=patient_records)

from app.utils import send_otp_email
@main_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            otp = user.generate_otp()  # Ensure this method exists in the User model
            send_otp_email(user.email, otp)  # Ensure this function sends the OTP email correctly
            flash('OTP has been sent to your email.', 'info')
            return redirect(url_for('main.verify_otp', user_id=user.id))  # Ensure verify_otp route exists
        flash('Email not found.', 'danger')
    return render_template('reset_password.html', form=form)

@main_bp.route('/verify_otp/<int:user_id>', methods=['GET', 'POST'])
def verify_otp(user_id):
    form = VerifyOTPForm()
    user = User.query.get_or_404(user_id)
    
    if form.validate_on_submit():
        if user.verify_otp(form.otp.data):
            flash('OTP verified. Please set a new password.', 'success')
            return redirect(url_for('main.reset_password_token', user_id=user.id))
        flash('Invalid or expired OTP.', 'danger')
    
    # Pass user object to the template
    return render_template('verify_otp.html', form=form, user=user)

@main_bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password_token(user_id):
    form = ResetPasswordForm()
    user = User.query.get_or_404(user_id)  # Fetch the user from the database using user_id
    if form.validate_on_submit():
        user.password = form.password.data  # Use the password setter to hash and store the password
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('main.login'))  # Redirect to login page after success
    return render_template('set_new_password.html', form=form, user=user)  # Pass user to template


@main_bp.route('/admin/users/management')
@login_required
def user_management():
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized access attempt to user management by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    # Fetch only users with the role of 'nurse' or 'doctor'
    users = User.query.filter(User.role.in_(['nurse', 'doctor'])).all()
    logger.info(f"User management accessed by {current_user.username}, {len(users)} users loaded")
    add_medic_form = CreateMedicForm()
    edit_user_form = EditUserForm()
    return render_template('user_management.html', users=users, add_medic_form=add_medic_form, edit_user_form=edit_user_form)


@main_bp.route('/admin/create-medic', methods=['POST'])
@login_required
def create_medic():
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized attempt to create medic by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    form = CreateMedicForm()
    if form.validate_on_submit():
        logger.info(f"Attempting to create medic with username: {form.username.data}, email: {form.email.data}, role: {form.role.data}, specialization: {form.specialization.data}")

        hashed_password = generate_password_hash('defaultpassword', method='pbkdf2:sha256')
        logger.info(f"Plaintext password for new medic: defaultpassword")

        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            logger.warning(f"Attempt to create medic with an existing email: {form.email.data}")
            flash('A user with this email already exists. Please use a different email.', 'danger')
            return redirect(url_for('main.user_management'))

        is_provider = form.role.data in ['doctor', 'nurse']
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                role=form.role.data,
                specialization=form.specialization.data,  # Capture specialization from the form
                is_provider=is_provider
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"New {form.role.data} created by {current_user.username}: Username={form.username.data}, Specialization={form.specialization.data}")
            flash(f'{form.role.data.capitalize()} created successfully.', 'success')
        except Exception as e:
            logger.error(f"Error creating medic: {str(e)}")
            flash('An error occurred while creating the medic. Please try again.', 'danger')
        return redirect(url_for('main.user_management'))

    logger.warning(f"Form submission failed for medic creation. Errors: {form.errors}")
    flash('Form submission failed. Please check the details.', 'danger')
    return redirect(url_for('main.user_management'))

@main_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Update user details based on form data
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']
        user.specialization = request.form['specialization']
        # Add any additional fields as needed
        
        db.session.commit()
        flash(f'User {user.username} updated successfully.', 'success')
        return redirect(url_for('main.user_management'))  # Adjust this route as per your setup

    return render_template('edit_user.html', user=user)
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Hash the password
            hashed_password = generate_password_hash(form.password.data)

            # Create new User
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password,
                role='patient'  # Assuming the role is 'patient' for new users
            )

            # Add the new user to the session and commit
            db.session.add(new_user)
            db.session.commit()  # Commit to generate the new user ID

            # Create new Patient record linked to the User
            new_patient = Patient(
                user_id=new_user.id,
                first_name=form.first_name.data,  # Assuming these fields are in your form
                last_name=form.last_name.data,
                dob=form.dob.data,  # Date of Birth
                phone_number=form.phone_number.data,
                address=form.address.data
            )

            # Add the new patient to the session and commit
            db.session.add(new_patient)
            db.session.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('main.login'))

        except Exception as e:
            # Log the exception and rollback in case of any error
            db.session.rollback()
            logger.exception(f"Error occurred during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', form=form)


@main_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted successfully.', 'success')
        logger.info(f"User {user_to_delete.username} deleted by {current_user.username}")
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('main.user_management'))

@main_bp.route('/admin/system/logs')
@login_required
def system_logs():
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized access attempt to system logs by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    logs = []  # Fetch logs from the database or logging system
    logger.info(f"System logs accessed by {current_user.username}")
    return render_template('system_logs.html', logs=logs)

@main_bp.route('/admin/analytics')
@login_required
def admin_analytics():
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized access attempt to analytics by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    analytics_data = []  # Process or query analytics data
    logger.info(f"Analytics accessed by {current_user.username}")
    return render_template('admin_analytics.html', analytics=analytics_data)

@main_bp.route('/admin/notifications')
@login_required
def notification_center():
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized access attempt to notification center by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    notifications = []  # Query notifications for the admin
    logger.info(f"Notification center accessed by {current_user.username}")
    return render_template('notification_center.html', notifications=notifications)


# Auth routes
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            # Redirect based on role
            role_redirect_map = {
                'admin': 'main.admin_dashboard',
                'doctor': 'main.doctor_dashboard',  # Ensure this matches the role name in your DB
                'nurse': 'main.nurse_dashboard',
                'patient': 'main.patient_dashboard'
            }
            redirect_url = role_redirect_map.get(user.role)
            if redirect_url:
                return redirect(url_for(redirect_url))
            else:
                flash('User role not recognized, redirecting to home.', 'warning')
                return redirect(url_for('main.index'))  # Fallback redirect
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.login'))

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            flash('Current password is incorrect. Please try again.', 'danger')
            return redirect(url_for('main.change_password'))

        current_user.password = generate_password_hash(form.new_password.data, method='pbkdf2:sha256')
        current_user.default_password = False
        db.session.commit()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('change_password.html', form=form)


@main_bp.route('/patients/<int:patient_id>/add', methods=['GET', 'POST'])
@login_required
def create_patient_record(patient_id):
    if current_user.role != 'doctor':
        flash('You do not have permission to add records.', 'danger')
        return redirect(url_for('main.list_patients'))

    patient = User.query.filter_by(id=patient_id, role='patient').first_or_404()
    # Logic to handle adding patient records
    return render_template('add_patient_record.html', patient=patient)

# Doctor routes
@main_bp.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        logger.warning(f"Unauthorized access attempt to doctor dashboard by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    # Query for appointments related to the current doctor
    appointments = (db.session.query(Appointment, AppointmentRequest, Patient)
                    .join(AppointmentRequest, Appointment.patient_request_id == AppointmentRequest.id)
                    .join(Patient, AppointmentRequest.patient_id == Patient.id)
                    .filter(Appointment.provider_id == current_user.id)
                    .all())

    logger.info(f"Doctor dashboard accessed by {current_user.username}")
    
    return render_template('doctor_dashboard.html', appointments=appointments)


@main_bp.route('/doctor/patient/<int:patient_id>/appointments', methods=['GET'])
@login_required
def view_patient_appointments(patient_id):
    if current_user.role != 'doctor':
        logger.warning(f"Unauthorized access attempt to view appointments for patient {patient_id} by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    # Fetch the patient using the patient_id
    patient = Patient.query.get_or_404(patient_id)

    # Fetch all AppointmentRequests and their corresponding Appointments for the patient
    appointments = (
        db.session.query(Appointment)
        .join(AppointmentRequest, Appointment.patient_request_id == AppointmentRequest.id)
        .filter(AppointmentRequest.patient_id == patient_id)
        .all()
    )

    if not appointments:
        flash('No appointments found for this patient.', 'warning')
        logger.info(f"Doctor {current_user.username} found no appointments for patient {patient_id}")
        return redirect(url_for('main.doctor_dashboard'))

    logger.info(f"Doctor {current_user.username} viewed appointments for patient {patient_id}")

    # Pass the appointments and patient details to the template
    return render_template('appointment_details.html', patient=patient, appointments=appointments)


@main_bp.route('/doctor/appointments/cancel/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    if current_user.role != 'doctor':
        logger.warning(f"Unauthorized access attempt to cancel appointment {appointment_id} by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    appointment = Appointment.query.get_or_404(appointment_id)

    # Get the associated AppointmentRequest using the patient_request_id
    appointment_request = AppointmentRequest.query.get(appointment.patient_request_id)

    if appointment_request:
        # Update the appointment status to 'cancelled'
        appointment.status = 'cancelled'

        # Update the AppointmentRequest status to 'cancelled'
        appointment_request.status = 'cancelled'

        db.session.commit()  # Commit the changes to both Appointment and AppointmentRequest tables

        logger.info(f"Doctor {current_user.username} cancelled appointment {appointment.id}")
        flash('Appointment cancelled successfully.', 'success')
    else:
        logger.error(f"AppointmentRequest not found for Appointment {appointment.id}")
        flash('Error: Associated appointment request not found.', 'danger')

    return redirect(url_for('main.doctor_dashboard'))  # Redirect to the doctor dashboard after cancellation


@main_bp.route('/doctor/admit_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def admit_patient(patient_id):
    # Find the patient in the database
    patient = Patient.query.get(patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Handle GET request to display the form
    if request.method == 'GET':
        # Retrieve available beds
        available_beds = Bed.query.filter_by(is_occupied=False).all()
        if not available_beds:
            flash('No available beds for admission.', 'warning')
            return redirect(url_for('main.doctor_dashboard'))

        # Render the admit patient form
        return render_template('admit_patient.html', patient=patient, available_beds=available_beds)

    # Handle POST request to admit the patient
    if request.method == 'POST':
        # Check if the patient is already admitted
        if patient.is_admitted:
            flash('Patient is already admitted.', 'warning')
            return redirect(url_for('main.doctor_dashboard'))

        # Retrieve form data
        bed_id = request.form['bed_id']
        expected_discharge_date = request.form['expected_discharge_date']
        reason_for_admission = request.form['reason_for_admission']

        # Retrieve selected bed
        selected_bed = Bed.query.get(bed_id)
        if not selected_bed or selected_bed.is_occupied:
            flash('Selected bed is unavailable.', 'danger')
            return redirect(url_for('main.doctor_dashboard'))

        # Assign bed to patient and create admission record
        try:
            # Mark the selected bed as occupied
            selected_bed.is_occupied = True

            # Create the admission record
            admission_record = AdmissionRecord(
                patient_id=patient.id,
                bed_id=selected_bed.id,
                doctor_id=current_user.id,
                admission_date=datetime.utcnow(),
                expected_discharge_date=expected_discharge_date,
                reason_for_admission=reason_for_admission
            )

            # Update patient admission status
            patient.is_admitted = True

            # Commit changes to the database
            db.session.add(admission_record)
            db.session.commit()

            flash('Patient admitted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while admitting the patient: {str(e)}', 'danger')

        return redirect(url_for('main.doctor_dashboard'))



@main_bp.route('/doctor/discharge_patient/<int:patient_id>', methods=['POST'])
@login_required
def discharge_patient(patient_id):
    # Find the patient in the database
    patient = Patient.query.get(patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Check if the patient is currently admitted
    if not patient.is_admitted:
        flash('Patient is not currently admitted.', 'warning')
        return redirect(url_for('main.doctor_dashboard'))

    # Logic for discharging the patient
    try:
        patient.is_admitted = False  # Set admission status
        # Optionally, update or create a discharge record
        # discharge_record = DischargeRecord(patient_id=patient.id, doctor_id=current_user.id)
        # db.session.add(discharge_record)

        db.session.commit()
        flash('Patient discharged successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while discharging the patient. Please try again.', 'danger')

    return redirect(url_for('main.doctor_dashboard'))


@main_bp.route('/nurse/patients/<int:patient_id>/record', methods=['GET', 'POST'])
@login_required
def nurse_update_patient_record(patient_id):
    if current_user.role != 'nurse':
        logger.warning(f"Unauthorized access attempt to update record for patient {patient_id} by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    patient = User.query.get_or_404(patient_id)
    form = UpdatePatientRecordForm()
    if form.validate_on_submit():
        record = PatientRecord(patient_id=patient.id, record_date=form.record_date.data, details=form.details.data)
        db.session.add(record)
        db.session.commit()
        logger.info(f"Nurse {current_user.username} updated medical record for patient {patient.username}")
        flash('Medical record updated successfully.', 'success')
        return redirect(url_for('main.nurse_dashboard'))

    return render_template('nurse_update_patient_record.html', form=form, patient=patient)


# Patient routes
@main_bp.route('/patient/dashboard')
@login_required
def patient_dashboard():
    # Verify that the current user is a patient
    if current_user.role != 'patient':
        logger.warning(f"Unauthorized access attempt to patient dashboard by {current_user.username}")
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    try:
        # Attempt to retrieve the patient data based on the user's ID
        logger.info(f"Attempting to retrieve patient data for user ID: {current_user.id}")
        patient = Patient.query.filter_by(user_id=current_user.id).first()

        if not patient:
            logger.warning(f"No patient record found for user {current_user.username}")
            flash('No patient record found for your account. Limited access to dashboard features.', 'warning')
            # Placeholder for missing patient record, allowing access to the dashboard template
            patient = type('Patient', (object,), {'first_name': 'Unknown', 'last_name': 'Unknown', 'id': None})

        logger.info(f"Patient {patient.first_name} {patient.last_name} dashboard accessed")
    except Exception as e:
        logger.error(f"Error retrieving patient data for user {current_user.username}: {e}")
        flash('Error retrieving your data. Please try again later.', 'danger')
        return redirect(url_for('main.index'))

    # Initialize empty lists for appointments, records, and prescriptions
    appointments, records, prescriptions = [], [], []

    try:
        # Proceed only if a valid patient ID exists
        if patient.id:
            # Retrieve all related data for the patient
            appointment_requests = AppointmentRequest.query.filter_by(patient_id=patient.id).all()
            appointment_ids = [request.id for request in appointment_requests]

            # Use eager loading for the `appointment_provider` relationship
            appointments = Appointment.query.filter(
                Appointment.patient_request_id.in_(appointment_ids)
            ).options(
                db.joinedload(Appointment.appointment_provider)  # Eagerly load provider data
            ).all()

            records = PatientRecord.query.filter_by(patient_id=patient.id).all()
            prescriptions = Prescription.query.filter_by(patient_id=patient.id).all()

            logger.info(f"Retrieved {len(appointments)} appointments, {len(records)} records, and {len(prescriptions)} prescriptions for patient {patient.first_name} {patient.last_name}")
        else:
            logger.warning("No patient ID found; unable to retrieve detailed records.")
    except Exception as e:
        logger.error(f"Error retrieving appointments/records/prescriptions for patient {patient.first_name} {patient.last_name}: {e}")
        flash('Error retrieving your appointments or medical records. Please try again later.', 'danger')

    return render_template(
        'patient_dashboard.html',
        patient=patient,
        appointments=appointments,
        records=records,
        prescriptions=prescriptions
    )




@main_bp.route('/patient/view-prescriptions')
@login_required
def view_prescriptions():
    # Fetch the patient info based on the current user's ID
    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()
    # Retrieve the prescriptions related to the patient
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()
    
    # Pass both the patient and prescriptions to the template
    return render_template('view_prescriptions.html', patient=patient, prescriptions=prescriptions)
from datetime import datetime

@main_bp.route('/patient/update-info', methods=['GET', 'POST'])
@login_required
def update_patient_info():
    # Fetch the patient's information based on the current user's ID
    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        # Update the patient's information based on the form data
        patient.phone_number = request.form.get('phone_number')
        patient.address = request.form.get('address')
        # Assuming email is linked to User
        patient.user.email = request.form.get('email')
        
        # Ensure the 'dob' is properly formatted before updating
        dob_string = request.form.get('dob')  # Get the DOB as a string (e.g., '2024-10-29')
        if dob_string:
            # Convert the string to a date object
            patient.dob = datetime.strptime(dob_string, '%Y-%m-%d').date()

        # Commit the changes to the database
        db.session.commit()

        flash('Your information has been updated successfully!', 'success')
        return redirect(url_for('main.patient_dashboard'))

    return render_template('update_patient_info.html', patient=patient)



@main_bp.route('/patient/view-medical-records')
@login_required
def view_medical_records():
    # Retrieve the patient based on the current user's ID
    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Fetch medical records associated with the patient
    records = MedicalRecord.query.filter_by(patient_id=patient.id).all()

    # Render the template with both the patient and records
    return render_template('view_medical_records.html', patient=patient, records=records)

from datetime import datetime
@main_bp.route('/patient/request-appointment', methods=['GET', 'POST'])
@login_required
def request_appointment():
    # Ensure the current user has a patient profile
    patient = current_user.patient_info
    if not patient:
        flash('You do not have a patient profile.', 'danger')
        return redirect(url_for('main.patient_dashboard'))

    # Fetch all doctor specializations for the selection dropdown
    doctor_specializations = db.session.query(User.specialization).filter(User.is_provider == True).distinct().all()
    specializations = [spec[0] for spec in doctor_specializations]  # Convert to a list of strings

    if request.method == 'POST':
        try:
            requested_time_str = request.form.get('requested_time')
            reason = request.form.get('reason')  # Optional field
            specialization_needed = request.form.get('specialization_needed')  # Get the specialization needed
            requested_time = datetime.fromisoformat(requested_time_str)  # Parse the date and time

            # Create new appointment request object
            appointment_request = AppointmentRequest(
                patient_id=patient.id,
                user_id=current_user.id,
                requested_time=requested_time,
                reason=reason,
                specialization_needed=specialization_needed,  # Include specialization
                status='pending'
            )

            # Save to the database
            db.session.add(appointment_request)
            db.session.commit()

            flash('Appointment request submitted successfully!', 'success')
            return redirect(url_for('main.patient_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting the appointment request: {str(e)}', 'danger')

    return render_template('request_appointment.html', specializations=specializations)


    
@main_bp.route('/patient/update_info', methods=['GET', 'POST'])
@login_required
def update_info():
    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        # Get the form data
        patient.user.email = request.form['email']
        patient.phone_number = request.form['phone_number']
        patient.dob = request.form['dob']
        patient.address = request.form['address']
        
        # Save changes
        db.session.commit()
        flash('Your information has been updated successfully!', 'success')
        return redirect(url_for('patient_dashboard'))

    return render_template('update_info.html', patient=patient)

from datetime import datetime

@main_bp.route('/doctor/schedule_appointment', methods=['POST'])
@login_required
def schedule_appointment_for_patient():
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    # Get the request_id from the form
    request_id = request.form.get('request_id')
    appointment_request = AppointmentRequest.query.get_or_404(request_id)  # Fetch the appointment request by ID

    # Fetch the patient details from the appointment request
    patient = Patient.query.get_or_404(appointment_request.patient_id)

    # Convert appointment_date from string to datetime
    appointment_date_str = request.form.get('appointment_date')
    try:
        appointment_date = datetime.fromisoformat(appointment_date_str)  # Convert to datetime object
    except ValueError:
        flash('Invalid date format. Please use the correct format.', 'danger')
        return redirect(url_for('main.view_patient', patient_id=patient.id))

    # Create the new appointment based on the submitted form data
    appointment = Appointment(
        patient_request_id=appointment_request.id,  # Link to the appointment request
        provider_id=current_user.id,  # The doctor as the provider
        appointment_date=appointment_date,  # Pass as datetime object
        notes=request.form.get('reason', '')  # Optional: get the reason if provided
    )

    # Add the appointment to the session and commit
    db.session.add(appointment)
    db.session.commit()

    flash('Appointment scheduled successfully!', 'success')

    # Redirect to the relevant dashboard based on the user's role
    if current_user.role == 'doctor':
        return redirect(url_for('main.doctor_dashboard'))
    elif current_user.role == 'nurse':
        return redirect(url_for('main.nurse_dashboard'))
    else:
        return redirect(url_for('main.index'))

from sqlalchemy import func

@main_bp.route('/nurse/assign_room/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def assign_room(patient_id):
    if current_user.role != 'nurse':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    patient = Patient.query.get_or_404(patient_id)

    # Get a list of all available rooms that are not full
    available_rooms = Room.query \
        .outerjoin(Patient, Room.id == Patient.room_id) \
        .group_by(Room.id) \
        .having(func.count(Patient.id) < Room.bed_count) \
        .all()

    # Debugging: Log the available rooms
    logging.debug(f"Available rooms count: {len(available_rooms)}")
    for room in available_rooms:
        logging.debug(f"Room {room.room_number} has {len(room.patients)} patients, Bed Count: {room.bed_count}")

    if request.method == 'POST':
        room_number = request.form.get('room_number')  # The room number selected by the nurse
        
        # Find the room based on the room number selected
        room = Room.query.filter_by(room_number=room_number).first()

        if room:
            # Count the number of patients in the room
            room_patients_count = Patient.query.filter_by(room_id=room.id).count()
            
            # Check if the room has space
            if room_patients_count < room.bed_count:
                patient.room_id = room.id  # Assign the selected room to the patient
                db.session.commit()  # Commit the changes to the database
                flash(f'Room {room.room_number} assigned to patient successfully!', 'success')
            else:
                flash(f'Room {room.room_number} is full.', 'danger')
        else:
            flash(f'Room {room_number} is invalid.', 'danger')

        return redirect(url_for('main.nurse_dashboard'))  # Redirect back to the nurse dashboard after assignment

    return render_template('assign_room.html', patient=patient, available_rooms=available_rooms)


@main_bp.route('/nurse/admit_patient/<int:patient_id>', methods=['POST'])
@login_required
def admit_patients(patient_id):
    if current_user.role != 'nurse':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    patient = Patient.query.get_or_404(patient_id)
    if not patient.is_admitted:
        patient.is_admitted = True  # Admit the patient
        
        # Create an AdmissionRecord entry
        admission_record = AdmissionRecord(
            patient_id=patient.id,
            doctor_id=current_user.id  # Assuming the current user is the admitting nurse/doctor
        )
        db.session.add(admission_record)
        db.session.commit()
        
        flash(f'Patient {patient.first_name} {patient.last_name} admitted successfully!', 'success')
    else:
        flash('Patient is already admitted.', 'warning')

    return redirect(url_for('main.list_patients_nurse'))


@main_bp.route('/nurse/discharge_patient/<int:patient_id>', methods=['POST'])
@login_required
def discharge_patients(patient_id):
    if current_user.role != 'nurse':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    patient = Patient.query.get_or_404(patient_id)
    if patient.is_admitted:
        patient.is_admitted = False  # Discharge the patient
        
        # Free up the room and bed
        if patient.room:
            patient.room.patients.remove(patient)
        if patient.bed:
            patient.bed.free_up()
        
        patient.room_id = None
        patient.bed_id = None

        # Create a DischargeRecord entry
        discharge_record = DischargeRecord(
            patient_id=patient.id,
            doctor_id=current_user.id  # Assuming the current user is the discharging nurse/doctor
        )
        db.session.add(discharge_record)
        db.session.commit()
        
        flash(f'Patient {patient.first_name} {patient.last_name} discharged successfully!', 'success')
    else:
        flash('Patient is not admitted.', 'warning')

    return redirect(url_for('main.list_patients_nurse'))



@main_bp.route('/assign_bed/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def assign_bed(patient_id):
    if current_user.role != 'nurse':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    patient = Patient.query.get_or_404(patient_id)

    # Get all beds in the patient's room that are not currently assigned to another patient
    available_beds = Bed.query.filter(
        Bed.room_id == patient.room_id,
        ~Patient.query.filter_by(bed_id=Bed.id).exists()  # Ensure the bed is unassigned
    ).all()

    # Check if there are any available beds
    if not available_beds:
        flash('No available beds in the selected room.', 'danger')
        return redirect(url_for('main.nurse_dashboard'))

    if request.method == 'POST':
        bed_number = request.form.get('bed_number')  # This will get the selected bed number from the form
        # Find the bed with the given bed_number
        bed = Bed.query.filter_by(bed_number=bed_number, room_id=patient.room_id).first()

        # Check if the bed is already occupied
        if bed and not Patient.query.filter_by(bed_id=bed.id).first():
            patient.bed_id = bed.id  # Assign the bed to the patient
            patient.is_admitted = True  # Mark the patient as admitted
            db.session.commit()  # Commit the changes to the database
            flash('Bed assigned successfully!', 'success')
        else:
            flash('The selected bed is already occupied.', 'danger')

        return redirect(url_for('main.nurse_dashboard'))  # Redirect to the nurse dashboard after assignment

    return render_template('assign_bed.html', patient=patient, available_beds=available_beds)


    
@main_bp.route('/prescription_report')
@login_required
def prescription_report():
    prescriptions = Prescription.query.all()  # Fetch all prescriptions
    return render_template('prescription_report.html', prescriptions=prescriptions)

@main_bp.route('/admissions_report')
@login_required
def admissions_report():
    admissions = AdmissionRecord.query.all()  # Fetch all admissions
    discharges = DischargeRecord.query.all()  # Fetch all discharges
    return render_template('admissions_report.html', admissions=admissions, discharges=discharges)

@main_bp.route('/health_metrics_report')
@login_required
def health_metrics_report():
    health_metrics = HealthMetrics.query.all()  # Fetch all health metrics data
    return render_template('health_metrics_report.html', health_metrics=health_metrics)

@main_bp.route('/operational_report')
@login_required
def operational_report():
    rooms = Room.query.all()  # Fetch room data
    bed_usage = Bed.query.all()  # Fetch bed usage data
    return render_template('operational_report.html', rooms=rooms, bed_usage=bed_usage)

@main_bp.route('/clinical_report')
@login_required
def clinical_report():
    records = PatientRecord.query.all()  # Fetch all clinical records
    return render_template('clinical_report.html', records=records)
@main_bp.route('/appointment_report')
@login_required
def appointment_report():
    appointments = Appointment.query.join(AppointmentRequest).join(Patient).all()
    return render_template('appointment_report.html', appointments=appointments)
@main_bp.route('/patient_report')
@login_required
def patient_report():
    patients = Patient.query.all()  # Fetch all patients
    return render_template('patient_report.html', patients=patients)

@main_bp.route('/doctor/view_appointment_requests/<int:patient_id>', methods=['GET'])
@login_required
def view_appointment_requests(patient_id):
    # Ensure the current user is a doctor
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    # Fetch the patient using the patient_id from the URL
    patient = Patient.query.get_or_404(patient_id)

    # Fetch the patient's appointment requests along with related user info
    appointment_requests = (
        AppointmentRequest.query
        .filter_by(patient_id=patient.id)  # Filter by the patient's ID
        .options(db.joinedload(AppointmentRequest.patient_requester))  # Eager load patient_requester (User) information
        .all()
    )

    # Render the template with the patient's requests and patient info
    return render_template(
        'view_appointment_requests.html',
        requests=appointment_requests,
        patient=patient
    )

@main_bp.route('/appointments', methods=['GET'])
@login_required
def appointments():
    # Fetch all appointment requests where the logged-in user is either a patient or a provider
    user_id = current_user.id  # Get the logged-in user's ID

    if current_user.role == 'patient':
        # If the logged-in user is a patient, fetch their appointment requests
        appointment_requests = AppointmentRequest.query.filter_by(user_id=user_id).all()
    elif current_user.role == 'doctor' or current_user.role == 'nurse':
        # If the logged-in user is a doctor or nurse, fetch appointment requests associated with them
        appointment_requests = AppointmentRequest.query.join(Patient).filter(
            Patient.user_id == user_id
        ).all()
    else:
        # Admin or other roles: Fetch all appointment requests
        appointment_requests = AppointmentRequest.query.all()

    # Pass the data to the template
    return render_template('appointments.html', appointment_requests=appointment_requests)
