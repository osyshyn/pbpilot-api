from core import BaseModelSchema


class ProfileInformationSchema(BaseModelSchema):
    """Profile information section of settings."""

    first_name: str
    last_name: str
    email: str
    lab_results_email: str
    phone_number: str
    company_name: str
    business_address: str


class LaboratoryDetailsSchema(BaseModelSchema):
    """Laboratory details sub-section."""

    laboratory_name: str = ''
    lab_account_number: str = ''
    street_address: str = ''
    city: str = ''
    state: str = ''
    zip_code: str = ''


class LaboratoryContactsSchema(BaseModelSchema):
    """Laboratory contacts sub-section."""

    lab_contact_email: str = ''
    lab_phone_number: str = ''


class LaboratoryAccreditationSchema(BaseModelSchema):
    """Laboratory accreditation sub-section."""

    accreditation_program: str = ''
    serial_numbers_certificates: str = ''


class LaboratoryTestingMethodSchema(BaseModelSchema):
    """Testing method and materials sub-section."""

    dust_wipe_medium_used: str = ''
    products_materials: str = ''
    standards_protocols: str = ''


class LaboratorySamplingTypesSchema(BaseModelSchema):
    """Sampling types sub-section."""

    all_sampling: bool = False
    dust_wipe: bool = True
    paint_chip: bool = False
    soil: bool = False
    water: bool = False


class LaboratoryInformationSchema(BaseModelSchema):
    """Laboratory information section of settings."""

    laboratory_details: LaboratoryDetailsSchema = LaboratoryDetailsSchema()
    contacts: LaboratoryContactsSchema = LaboratoryContactsSchema()
    accreditation: LaboratoryAccreditationSchema = (
        LaboratoryAccreditationSchema()
    )
    testing_method_and_materials: LaboratoryTestingMethodSchema = (
        LaboratoryTestingMethodSchema()
    )
    sampling_types: LaboratorySamplingTypesSchema = (
        LaboratorySamplingTypesSchema()
    )


class PreferencesSchema(BaseModelSchema):
    """Preferences section of settings."""

    theme: str = 'Dark'
    date_format: str = 'MM/DD/YYYY'
    start_of_the_calendar_week: str = 'Monday'
    timezone: str = 'Eastern Time'


class SettingsResponseSchema(BaseModelSchema):
    """Top-level settings response schema."""

    profile_information: ProfileInformationSchema
    laboratory_information: LaboratoryInformationSchema = (
        LaboratoryInformationSchema()
    )
    preferences: PreferencesSchema = PreferencesSchema()
