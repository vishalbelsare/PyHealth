from pyhealth.data import Patient


def categorize_los(days: int):
    """Categorize length of stay into 10 categories.

    One for ICU stays shorter than a day, seven day-long categories for each day of
    the first week, one for stays of over one week but less than two,
    and one for stays of over two weeks.

    Args:
        days: int, length of stay in days

    Returns:
        category: int, category of length of stay
    """
    # ICU stays shorter than a day
    if days < 1:
        return 0
    # each day of the first week
    elif 1 <= days <= 7:
        return days
    # stays of over one week but less than two
    elif 7 < days <= 14:
        return 8
    # stays of over two weeks
    else:
        return 9


def length_of_stay_prediction_mimic3_fn(patient: Patient):
    """
    Length of stay prediction aims at predicting the length of stay (in days) of the
    current hospital visit based on the clinical information from the visit
    (e.g., conditions and procedures).

    Process a single patient for the length-of-stay prediction task.

    Args:
        patient: a Patient object.

    Returns:
        samples: a list of samples, each sample is a dict with patient_id, visit_id,
            and other task-specific attributes as key.

    Note that we define the task as a multi-class classification task.
    
    **Example:**
        >>> from pyhealth.datasets import MIMIC3Dataset
        >>> mimic3_ds = MIMIC3Dataset(
        ...    root="/srv/local/data/physionet.org/files/mimiciii/1.4",
        ...    tables=["DIAGNOSES_ICD", "PROCEDURES_ICD", "PRESCRIPTIONS"],
        ...    code_mapping={"ICD9CM": "CCSCM"},
        ... )
        >>> from pyhealth.tasks import length_of_stay_prediction_mimic3_fn
        >>> dataset.set_task(length_of_stay_prediction_mimic3_fn) # set task
        >>> dataset.samples[0] # exampe of an training sample
        [{'visit_id': '130744', 'patient_id': '103', 'conditions': [['42', '109', '19', '122', '98', '663', '58', '51']], 'procedures': [['1']], 'label': 4}]
        
    """
    samples = []

    for visit in patient:

        conditions = visit.get_code_list(table="DIAGNOSES_ICD")
        procedures = visit.get_code_list(table="PROCEDURES_ICD")
        drugs = visit.get_code_list(table="PRESCRIPTIONS")
        # exclude: visits without condition, procedure, and drug code
        if len(conditions) + len(procedures) + len(drugs) == 0:
            continue

        los_days = (visit.discharge_time - visit.encounter_time).days
        los_category = categorize_los(los_days)

        # TODO: should also exclude visit with age < 18
        samples.append(
            {
                "visit_id": visit.visit_id,
                "patient_id": patient.patient_id,
                "conditions": [conditions],
                "procedures": [procedures],
                "drugs": [drugs],
                "label": los_category,
            }
        )
    # no cohort selection
    return samples


def length_of_stay_prediction_mimic4_fn(patient: Patient):
    """
    Length of stay prediction aims at predicting the length of stay (in days) of the
    current hospital visit based on the clinical information from the visit
    (e.g., conditions and procedures).

    Process a single patient for the length-of-stay prediction task.

    Args:
        patient: a Patient object.

    Returns:
        samples: a list of samples, each sample is a dict with patient_id, visit_id,
            and other task-specific attributes as key.

    Note that we define the task as a multi-class classification task.
    
    **Example:**
        >>> from pyhealth.datasets import MIMIC4Dataset
        >>> mimic4_ds = MIMIC4Dataset(
        ...     root="/srv/local/data/physionet.org/files/mimiciv/2.0/hosp",
        ...     tables=["diagnoses_icd", "procedures_icd"],
        ...     code_mapping={"ICD10PROC": "CCSPROC"},
        ... )
        >>> from pyhealth.tasks import length_of_stay_prediction_mimic4_fn
        >>> dataset.set_task(length_of_stay_prediction_mimic4_fn) # set task
        >>> dataset.samples[0] # exampe of an training sample
        [{'visit_id': '130744', 'patient_id': '103', 'conditions': [['42', '109', '19', '122', '98', '663', '58', '51']], 'procedures': [['1']], 'label': 2}]
        
        
    """
    samples = []

    for visit in patient:

        conditions = visit.get_code_list(table="diagnoses_icd")
        procedures = visit.get_code_list(table="procedures_icd")
        drugs = visit.get_code_list(table="prescriptions")
        # exclude: visits without condition, procedure, and drug code
        if len(conditions) + len(procedures) + len(drugs) == 0:
            continue

        los_days = (visit.discharge_time - visit.encounter_time).days
        los_category = categorize_los(los_days)

        # TODO: should also exclude visit with age < 18
        samples.append(
            {
                "visit_id": visit.visit_id,
                "patient_id": patient.patient_id,
                "conditions": [conditions],
                "procedures": [procedures],
                "drugs": [drugs],
                "label": los_category,
            }
        )
    # no cohort selection
    return samples


def length_of_stay_prediction_eicu_fn(patient: Patient):
    """
    Length of stay prediction aims at predicting the length of stay (in days) of the
    current hospital visit based on the clinical information from the visit
    (e.g., conditions and procedures).

    Process a single patient for the length-of-stay prediction task.

    Args:
        patient: a Patient object.

    Returns:
        samples: a list of samples, each sample is a dict with patient_id, visit_id,
            and other task-specific attributes as key.

    Note that we define the task as a multi-class classification task.
    
    **Example:**
        >>> from pyhealth.datasets import eICUDataset
        >>> eicu_ds = eICUDataset(
        ...     root="/srv/local/data/physionet.org/files/eicu-crd/2.0",
        ...     tables=["diagnosis", "medication"],
        ...     code_mapping={},
        ...     dev=True
        ... )
        >>> from pyhealth.tasks import length_of_stay_prediction_eicu_fn
        >>> dataset.set_task(length_of_stay_prediction_eicu_fn) # set task
        >>> dataset.samples[0] # exampe of an training sample
        [{'visit_id': '130744', 'patient_id': '103', 'conditions': [['42', '109', '98', '663', '58', '51']], 'procedures': [['1']], 'label': 5}]
        
        
    """
    samples = []

    for visit in patient:

        conditions = visit.get_code_list(table="diagnosis")
        procedures = visit.get_code_list(table="physicalExam")
        drugs = visit.get_code_list(table="medication")
        # exclude: visits without condition, procedure, and drug code
        if len(conditions) + len(procedures) + len(drugs) == 0:
            continue

        los_days = (visit.discharge_time - visit.encounter_time).days
        los_category = categorize_los(los_days)

        # TODO: should also exclude visit with age < 18
        samples.append(
            {
                "visit_id": visit.visit_id,
                "patient_id": patient.patient_id,
                "conditions": [conditions],
                "procedures": [procedures],
                "drugs": [drugs],
                "label": los_category,
            }
        )
    # no cohort selection
    return samples


def length_of_stay_prediction_omop_fn(patient: Patient):
    """
    Length of stay prediction aims at predicting the length of stay (in days) of the
    current hospital visit based on the clinical information from the visit
    (e.g., conditions and procedures).

    Process a single patient for the length-of-stay prediction task.

    Args:
        patient: a Patient object.

    Returns:
        samples: a list of samples, each sample is a dict with patient_id, visit_id,
            and other task-specific attributes as key.

    Note that we define the task as a multi-class classification task.
    
    **Examples:**
        >>> from pyhealth.datasets import OMOPDataset
        >>> omop_ds = OMOPDataset(
        ...     root="https://storage.googleapis.com/pyhealth/synpuf1k_omop_cdm_5.2.2",
        ...     tables=["condition_occurrence", "procedure_occurrence"],
        ...     code_mapping={},
        ... )
        >>> from pyhealth.tasks import length_of_stay_prediction_omop_fn
        >>> dataset.set_task(length_of_stay_prediction_eicu_fn) # set task
        >>> dataset.samples[0] # exampe of an training sample
        [{'visit_id': '130744', 'patient_id': '103', 'conditions': [['42', '109', '98', '663', '58', '51']], 'procedures': [['1']], 'label': 7}]
        
    """
    samples = []

    for visit in patient:

        conditions = visit.get_code_list(table="condition_occurrence")
        procedures = visit.get_code_list(table="procedure_occurrence")
        drugs = visit.get_code_list(table="drug_exposure")
        # exclude: visits without condition, procedure, and drug code
        if len(conditions) + len(procedures) + len(drugs) == 0:
            continue

        los_days = (visit.discharge_time - visit.encounter_time).days
        los_category = categorize_los(los_days)

        # TODO: should also exclude visit with age < 18
        samples.append(
            {
                "visit_id": visit.visit_id,
                "patient_id": patient.patient_id,
                "conditions": [conditions],
                "procedures": [procedures],
                "drugs": [drugs],
                "label": los_category,
            }
        )
        # no cohort selection
    return samples


if __name__ == "__main__":
    # from pyhealth.datasets import MIMIC3Dataset
    #
    # dataset = MIMIC3Dataset(
    #     root="/srv/local/data/physionet.org/files/mimiciii/1.4",
    #     tables=["DIAGNOSES_ICD", "PROCEDURES_ICD", "PRESCRIPTIONS"],
    #     dev=True,
    #     code_mapping={"ICD9CM": "CCSCM", "NDC": "ATC"},
    #     refresh_cache=False,
    # )
    # dataset.set_task(task_fn=length_of_stay_prediction_mimic3_fn)
    # dataset.stat()
    # print(dataset.available_keys)

    # from pyhealth.datasets import MIMIC4Dataset
    #
    # dataset = MIMIC4Dataset(
    #     root="/srv/local/data/physionet.org/files/mimiciv/2.0/hosp",
    #     tables=["diagnoses_icd", "procedures_icd", "prescriptions"],
    #     dev=True,
    #     code_mapping={"NDC": "ATC"},
    #     refresh_cache=False,
    # )
    # dataset.set_task(task_fn=length_of_stay_prediction_mimic4_fn)
    # dataset.stat()
    # print(dataset.available_keys)

    # from pyhealth.datasets import eICUDataset
    #
    # dataset = eICUDataset(
    #     root="/srv/local/data/physionet.org/files/eicu-crd/2.0",
    #     tables=["diagnosis", "medication", "physicalExam"],
    #     dev=True,
    #     refresh_cache=False,
    # )
    # dataset.set_task(task_fn=length_of_stay_prediction_eicu_fn)
    # dataset.stat()
    # print(dataset.available_keys)

    from pyhealth.datasets import OMOPDataset

    dataset = OMOPDataset(
        root="/srv/local/data/zw12/pyhealth/raw_data/synpuf1k_omop_cdm_5.2.2",
        tables=["condition_occurrence", "procedure_occurrence", "drug_exposure"],
        dev=True,
        refresh_cache=False,
    )
    dataset.set_task(task_fn=length_of_stay_prediction_omop_fn)
    dataset.stat()
    print(dataset.available_keys)
