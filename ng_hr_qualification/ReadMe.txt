Modification to HR (ng_hr_qualification)

Human Resources/Employee:

- We need to add a tab for “Qualifications”. In this tab, we will provide sections and fields as follows:

Academic Qualifications: Here will will have the following columns (Degree, Subject, Institution, Date)

For each employee, we will need to complete the section for each of these columns.
- We should be able to enter as many records as possible (so give feature to add line of records)
- We should select Degree, Subject, Institution in a list. So these needs to be added for setup under HR/Configuration

Schools Attended: Here we will request for schools attended and we will have the following columns (School or Institution, Start Date, End Date)

- Same Institution listing as indicated under Academic Qualification above)
Professional Qualifications:

Here we need the following columns (Qualifications, Awarding Organization, Date)

- Qualification here is not academic. It is professional qualification and different from Degree. It should be setup in Configuration so that we can select it from a list
- Awarding organization will be a text field. We don't need to set this up in configuration
We may need to add the above in Human Resources/Recruitment/Applicant. There is some information on Qualification there in the Job Info tab, but it is not enough.

Actually, most of the information on qualification shown in 1) above are more relevant for Applicants. This will allow us to search for applications in the database matching some qualification criteria. But we need to add this to the new Qualification tab in HR/Employee so that even employees can be searched for these qualification information
Where this information is entered for application and the applicant is hired, then we will simply copy the same information to the the qualification tab of employees
We need to add the following fields in HR/Recruitment/Applicant

- Gender
- Date of Birth

The Date of Birth will be used to calculate age of the applicant. So at any point in time, I should be able to search by Age etc
The information here will be automatically copied to the employee details when the applicant is hired. These fields are already in HR/Employee

We need search on Applicants for the following:
- Academic Qualification
- Professional Qualification
- Degree
- Institution
- Years of Experience (where can we capture this?)


6. We can call this module ng_hr_qualification

