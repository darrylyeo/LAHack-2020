import csv
from sys import argv
from datetime import date
from grakn.client import GraknClient


def parseDate(dateStr):
	month, day, year = map(
		lambda s: int(''.join(c for c in s if c.isdigit())[:4]),
		dateStr.split('/')[:3]
	)
	
	while True:
		try:
			return date(year, month, min(day, 1))
		except:
			day -= 1


def queryInsertPatientRecord(row):
	groupID, patientID, accountNumber, firstName, middleInitial, lastName, birthDate, sex, currentStreet1, currentStreet2, currentCity, currentState, currentZipCode, previousFirstName, previousMiddleInitial, previousLastName, previousStreet1, previousStreet2, previousCity, previousState, previousZipCode = (
		row[prop] for prop in
		('GroupID', 'PatientID', 'Patient Acct #', 'First Name', 'MI', 'Last Name', 'Date of Birth', 'Sex', 'Current Street 1', 'Current Street 2', 'Current City', 'Current State', 'Current Zip Code', 'Previous First Name', 'Previous MI', 'Previous Last Name', 'Previous Street 1', 'Previous Street 2', 'Previous City', 'Previous State', 'Previous Zip Code')
	)

	return '''
		insert
		
			$person isa person,
				has first-name "{firstName}",
				has middle-initial "{middleInitial}",
				has last-name "{lastName}",
				has birth-date {birthDate},
				has sex "{sex}";
			
			$account isa account,
				has account-number "{accountNumber}";
			
			$holds-account (
				account-holder: $person,
				patient-account: $account
			) isa holds-account;
		
			$current-address isa address,
				has street-1 "{currentStreet1}",
				has street-2 "{currentStreet2}",
				has city "{currentCity}",
				has state "{currentState}",
				has zip-code "{currentZipCode}";
			
			$previous-address isa address,
				has street-1 "{previousStreet1}",
				has street-2 "{previousStreet2}",
				has city "{previousCity}",
				has state "{previousState}",
				has zip-code "{previousZipCode}";
			

		# Relations
		
			$lives-at-address (
				person-with-address: $person,
				place-lived: $current-address
			) isa lives-at-address,
				has is-current true; # Infer?

			$lived-at-address (
				person-with-address: $person,
				place-lived: $previous-address
			) isa lives-at-address,
				has is-current false; # Infer?

			$patient-record (
				patient: $person,
				holds-account-in-record: $holds-account,
				lives-at-address-in-record: $lives-at-address,
				lived-at-address-in-record: $lived-at-address
			) isa patient-record;
	'''.format(
		accountNumber = accountNumber,
		firstName = firstName,
		middleInitial = middleInitial,
		lastName = lastName,
		birthDate = parseDate(birthDate),
		sex = sex,
		currentStreet1 = currentStreet1,
		currentStreet2 = currentStreet2, 
		currentCity = currentCity, 
		currentState = currentState, 
		currentZipCode = currentZipCode, 
		previousFirstName = previousFirstName, 
		previousMiddleInitial = previousMiddleInitial, 
		previousLastName = previousLastName, 
		previousStreet1 = previousStreet1, 
		previousStreet2 = previousStreet2, 
		previousCity = previousCity, 
		previousState = previousState, 
		previousZipCode = previousZipCode
	)



def main(keyspace = 'office_ally_patients', dataPath = 'sample-data/Patient Matching Data.csv'):
	print('Starting database client...')

	with GraknClient(uri='localhost:48555') as client:
		print('Starting database session...')

		with client.session(keyspace=keyspace) as session:
			print('Starting write transaction...')

			with session.transaction().write() as transaction:
				print('Importing data from "{dataPath}"...'.format(dataPath=dataPath))

				with open(dataPath) as csvfile:
					for row in csv.DictReader(csvfile):
						print('Inserting:', dict(row))
						insert_iterator = transaction.query(
							queryInsertPatientRecord(row)
						)
				
				transaction.commit()
			
			print('Closing database session...')
			## Close session
		
		print('Closing database client...')
		## Close client

	print('Successfully imported.')


if __name__ == '__main__':
	main(*argv[1:])
